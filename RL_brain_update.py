import numpy as np
import tensorflow as tf
from random import choice
class DeepQNetwork(object):
    def __init__(
            self,
            n_action=64,
            n_features=64,
            learning_rate=0.01,
            reward_decay=0.9,
            e_greedy=0.9,
            replace_target_iter=300,
            memory_size=500,
            batch_size=32,
            e_greedy_increment=None,
            output_graph=False,
    ):
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.epsilon_increment = e_greedy_increment
        self.epsilon = 0 if e_greedy_increment is not None else self.epsilon_max
        # total learning step
        self.learn_step_counter = 0

        # initialize zero memory [s, a, r, s_]
        self.memory = np.zeros((self.memory_size, n_features * 2 + 1))
        
        self.sess = tf.Session()
        # consist of [target_net, evaluate_net]
        
        self._create_input()
        
        self.eval_var_scope = "eval_net"
        with tf.variable_scope(self.eval_var_scope):
            self.q_eval = self._create_eval_net(inputstate=self.s)
                
        self.target_var_scope = "target_net"
        with tf.variable_scope(self.target_var_scope):
            self.q_next = -self._create_target_net(inputstate=-self.s_)
        
        with tf.variable_scope('q_target'):
            q_target = self.r + self.gamma * self.q_next   # shape=(None, )
            self.q_target = tf.stop_gradient(q_target)
        with tf.variable_scope('loss'):
            self.loss = tf.reduce_mean(tf.squared_difference(self.q_target, self.q_eval, name='TD_error'))
        with tf.variable_scope('train'):
            self._train_op = tf.train.RMSPropOptimizer(self.lr).minimize(self.loss)
            
        
        t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.target_var_scope)
        e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.eval_var_scope)
        with tf.variable_scope('soft_replacement'):
            self.target_replace_op = [tf.assign(t, e) for t, e in zip(t_params, e_params)]
        
        if output_graph:
            # $ tensorboard --logdir=logs
            # tf.train.SummaryWriter soon be deprecated, use following
            tf.summary.FileWriter("logs/", self.sess.graph)

        self.sess.run(tf.global_variables_initializer())
        self.cost_his = []
        
    def _create_input(self):
        self.s = tf.placeholder(tf.float32, [None, self.n_features], name='s')  # input State
        self.s_ = tf.placeholder(tf.float32, [None, self.n_features], name='s_')  # input Next State
        self.r = tf.placeholder(tf.float32, [None, ], name='r')  # input Reward
        self.a = tf.placeholder(tf.int32, [None, 2], name='a')  # input Action
        
    def _create_eval_net(self,inputstate):
        
        w_initializer, b_initializer = tf.random_normal_initializer(0., 0.1), tf.constant_initializer(0.1)
        #
        channel=16
        #first conv layer
        x_image=tf.reshape(inputstate,[-1,8,8,1])
        weight_conv=tf.Variable(tf.truncated_normal([3,3,1,channel],stddev=0.1))
        b_conv=tf.Variable(tf.constant(0.1,shape=[channel]))
        h_conv=tf.nn.relu(tf.nn.conv2d(x_image,weight_conv,strides=[1,1,1,1],padding='SAME')+b_conv)
        h_pool = tf.nn.max_pool(h_conv,ksize=[1,2,2,1],strides=[1,1,1,1],padding='SAME')   
        
        #second conv layer
        weight_conv2=tf.Variable(tf.truncated_normal([3,3,channel,channel*2],stddev=0.1))
        b_conv2=tf.Variable(tf.constant(0.1,shape=[channel*2]))
        h_conv2=tf.nn.relu(tf.nn.conv2d(h_pool,weight_conv2,strides=[1,1,1,1],padding='SAME')+b_conv2)
        h_pool2 = tf.nn.max_pool(h_conv2,ksize=[1,2,2,1],strides=[1,1,1,1],padding='SAME')  

        h_pool_flat=tf.reshape(h_pool2,[-1,8*8*channel*2])
        a1=tf.layers.dense(h_pool_flat,units=300, 
                              activation=tf.nn.relu, kernel_initializer=w_initializer,
                              bias_initializer=b_initializer, 
                              name='hidden_layer1')
        
        a2=tf.layers.dense(a1,units=150, 
                              activation=tf.nn.relu, kernel_initializer=w_initializer,
                              bias_initializer=b_initializer, 
                              name='hidden_layer2')
        
#        a3=tf.layers.dense(a2,units=50, 
#                              activation=tf.nn.relu, kernel_initializer=w_initializer,
#                              bias_initializer=b_initializer, 
#                              name='hidden_layer3')
        
        value=tf.layers.dense(a2,units=1, 
                              activation=tf.nn.tanh, kernel_initializer=w_initializer,
                              bias_initializer=b_initializer, 
                              name='evaluation')
        return value
        
            
    def _create_target_net(self,inputstate):
        
        return self._create_eval_net(inputstate)
        
    
    def store_transition(self, state, action, reward, state_):
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0
        s = state.reshape([1,-1])
        s_ = state_.reshape([1,-1])
        reward=np.array([reward]).reshape([1,-1])
        transition = np.hstack((s, reward, s_))
        # replace the old memory with new memory
        index = self.memory_counter % self.memory_size
        self.memory[index, :] = transition
        self.memory_counter += 1
        
    def choose_action(self, chess):
        actionspace=chess.find_action_space()
        actions_value_space=np.zeros(len(actionspace))
        if np.random.uniform() < self.epsilon:
            for i in range(len(actionspace)):
                state=chess.take_action(actionspace[i],realy=False).reshape([1,-1])
            # forward feed the observation and get q value for every actions
                actions_value_space[i]=(1-self.sess.run(self.q_eval, feed_dict={self.s: -state}))
            action = actionspace[np.argmax(actions_value_space)]
        else:
            action = choice(actionspace)
        return action
    
    def learn(self):
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.sess.run(self.target_replace_op)
            print('\ntarget_params_replaced\n')

        # sample batch memory from all memory
        if self.memory_counter > self.memory_size:
            sample_index = np.random.choice(self.memory_size, size=self.batch_size)
        else:
            sample_index = np.random.choice(self.memory_counter, size=self.batch_size)
        batch_memory = self.memory[sample_index, :]

        _, cost = self.sess.run(
            [self._train_op, self.loss],
            feed_dict={
                self.s: batch_memory[:, :self.n_features],
                self.r: batch_memory[:, -self.n_features-1],
                self.s_: batch_memory[:, -self.n_features:],
            })

        self.cost_his.append(cost)

        # increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        self.learn_step_counter += 1
        
    def plot_cost(self):
        import matplotlib.pyplot as plt
        plt.plot(np.arange(len(self.cost_his)), self.cost_his)
        plt.ylabel('Cost')
        plt.xlabel('training steps')
        plt.show()