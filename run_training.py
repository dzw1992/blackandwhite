#%%
from env_blackandwhite import BlackAndWhite
from RL_brain import DeepQNetwork
import random
import tensorflow as tf
import numpy as np

step = 0
savemodel=False
RL=DeepQNetwork(output_graph=True)
saver = tf.train.Saver() 
#%%
samplex=np.zeros([3000,64])
sampley=np.zeros([3000,1])
for episode in range(3000):
    A=BlackAndWhite()
    done=False
    while not done:
        _,reward,done=A.randomAImove()
    samplex[episode,:],sampley[episode]=A.chessBoard.reshape([1,-1]),(reward+1)/2
np.save("samplex.npy", samplex)
np.save("sampley.npy", sampley)
#%%
from sklearn.model_selection import train_test_split
samplex=np.load('samplex.npy')
sampley=np.load('sampley.npy')
x_train,y_train,x_test,y_test=train_test_split(samplex,sampley,test_size = 0.2)
RL.pre_train(x_train,y_train)
predict=RL.sess.run(RL.q_eval,feed_dict={RL.s:x_test})
print(np.count_nonzero(predict[y_test==1]<0.9))


#%%
for episode in range(1000):
    if episode%100==0:
        print(episode)
    if (episode+1)%1000==0 and savemodel:
        saver.save(RL.sess, "Model/model"+str(int(episode/10000))+".ckpt")  
    # initial observation
    chess=BlackAndWhite()
    blackOrWhite=(random.randint(0,1)*2-1)
    done=False
    chesslist=[]
    chesslist2=[]
    while True:
        # fresh env
        BW=chess.blackOrWhite
        chessBoard=chess.chessBoard
        # RL choose action based on observation
        action = RL.choose_action(chess)

        # RL take action and get next observation and reward
        chessBoard_,reward,done=chess.take_action(action)
        
        # break while loop when end of this episode
        RL.store_transition(state=chessBoard*BW, reward=reward, state_=chessBoard_*BW)
        if done:
            break
        step+=1
    if (step > 400):
        RL.learn()
# end of game
print('game over')
#%%
import numpy as np
sample_index = np.random.choice(RL.memory_size, 1)
memory=RL.memory[sample_index,:][0]
print(memory[0:64].reshape([8,8]))
print(memory[64])
print(memory[-64:].reshape([8,8]))
print(RL.sess.run(RL.q_target,feed_dict={RL.s_:memory[0:64].reshape([-1,64]),RL.r:memory[64].reshape([-1])}))
#%%
A=BlackAndWhite()
done=False
while not done:
    print(A.chessBoard)
    if 1==A.blackOrWhite:
        print(RL.sess.run(RL.q_eval,feed_dict={RL.s:A.chessBoard.reshape([1,-1])}))
        _,_,done=A.take_action(RL.choose_action(A))
    else:
        print(RL.sess.run(RL.q_eval,feed_dict={RL.s:-A.chessBoard.reshape([1,-1])}))
        _,_,done=A.randomAImove()
        
#RL.plot_cost()

#%%
for v in [5,6,7,8,9]:
    RL.sess.close()
    RL.sess=tf.Session()
    saver.restore(RL.sess, "Model/model"+str(int(v))+".ckpt")
    episode=500;
    scoreWhite=0;
    for i in range(episode):
        A=BlackAndWhite()
        done=False
        while not done:
            if 1==A.blackOrWhite:
                _,_,done=A.take_action(RL.choose_action(A))
            else:
                _,_,done=A.randomAImove()
            
        score=A.get_score()
        #    print(actionSpace)
        #    print(action)
        #    print(A.chessBoard)
        if score>0:
            scoreWhite+=1
    print('White win %d times'%scoreWhite)

#%%
import tensorflow as tf
saver = tf.train.Saver()  
saver.save(RL.sess, "Model/model.ckpt")  
A=BlackAndWhite()
for i in range(60):
    A.randomAImove()
print(RL.sess.run(RL.q_eval,feed_dict={RL.s:A.chessBoard.reshape([1,-1])}))

#%%
RL.sess.close()
RL.sess=tf.Session()
saver.restore(RL.sess, "Model/model.ckpt")
print(RL.sess.run(RL.q_eval,feed_dict={RL.s:A.chessBoard.reshape([1,-1])}))
#%%
reader = tf.train.NewCheckpointReader('Model/model.ckpt')  
all_variables = reader.get_variable_to_shape_map()  
w1 = reader.get_tensor("eval_net/e1/kernel")
print(w1)
#%%chech memory
import numpy as np
a=random.choice(RL.memory)
s=np.reshape(a[0:64],[8,8])
print(a[64])
s_=np.reshape(a[-64:],[8,8])
s[np.abs(s-s_)==1]+=100
print(s)
print(s_)