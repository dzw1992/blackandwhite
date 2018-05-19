
#%%
from env_blackandwhite import BlackAndWhite
from RL_brain_update import DeepQNetwork
import random

step = 0
RL=DeepQNetwork(output_graph=True)
 #%%
for episode in range(10):
    # initial observation
    chess=BlackAndWhite()
    done=False
    while True:
        # fresh env
        bw=chess.blackOrWhite
        chessBoard=chess.chessBoard
        # RL choose action based on observation
        action = RL.choose_action(chess)
        # RL take action and get next observation and reward
        chessBoard_,reward,done=chess.take_action(action)
        
        RL.store_transition(state=chessBoard*bw, action=action, reward=reward, state_=chessBoard_*bw)
        if (step > 200) and (step % 5 == 0):
            RL.learn()

        if done:
            break
        step+=1
# end of game
print('game over')

#%%
episode=200;
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
    print(score,i)
    #    print(actionSpace)
    #    print(action)
    #    print(A.chessBoard)
    if score>0:
        scoreWhite+=1
print('White win %d times'%scoreWhite)
