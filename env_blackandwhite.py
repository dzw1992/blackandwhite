
import numpy as np
from random import choice
global direction
direction=[[-1,0],
          [-1,1],
          [0,1],
          [1,1],
          [1,0],
          [1,-1],
          [0,-1],
          [-1,-1]]
class BlackAndWhite(object):
    def __init__(self,chessBoard=None,blackOrWhite=1):
        self.blackOrWhite=blackOrWhite
        if chessBoard==None:
            self.chessBoard=np.zeros([8,8],dtype=np.int8)
            self.chessBoard[3][3:5]=1,-1
            self.chessBoard[4][3:5]=-1,1
        else:
            self.chessBoard=chessBoard
        
    def is_direction_OK(self,action,i):
        deltai=direction[i][0]
        deltaj=direction[i][1]
        idx_i=action[0]
        idx_j=action[1]
        chessBoard=self.chessBoard*self.blackOrWhite
        if idx_i+deltai<0 or idx_i+deltai>7 \
          or idx_j+deltaj<0 or idx_j+deltaj>7 \
          or chessBoard[idx_i+deltai][idx_j+deltaj]!=-1:
            return False
        while idx_i+deltai<=7 and idx_i+deltai>=0 \
          and idx_j+deltaj<=7 and idx_j+deltaj>=0 \
          and chessBoard[idx_i+deltai][idx_j+deltaj]==-1:
            idx_i+=deltai
            idx_j+=deltaj
        if idx_i+deltai<0 or idx_i+deltai>7 \
          or idx_j+deltaj<0 or idx_j+deltaj>7:
            return False
        if chessBoard[idx_i+deltai][idx_j+deltaj]==1:
            return True
        else:
            return False
        
    def find_direction(self,action=[0,0]):
        global direction
        if self.chessBoard[action[0]][action[1]]!=0:
            return []
        else:
            idx_direction=[]
            for i in range(8):
                if self.is_direction_OK(action,i):
                    idx_direction.append(i)
        return idx_direction
               
                
    def find_action_space(self):
        actionSpace=[]
        for i in range(8):
            for j in range(8):
                if self.find_direction(action=[i,j]):
                    actionSpace.append([i,j])
        return actionSpace
    
    def isGameOver(self):
        if self.find_action_space():
            return False
        else:
            self.blackOrWhite=-self.blackOrWhite
            if self.find_action_space():
                self.blackOrWhite=-self.blackOrWhite
                return False
            else:
                return True
        
    def take_action(self,action,realy=True):
        if not (action in self.find_action_space()):
            return None
        chessBoard=self.chessBoard*self.blackOrWhite
        idx_direction=self.find_direction(action=action)
        chessBoard[action[0]][action[1]]=1
        for i in idx_direction:
            deltai=direction[i][0]
            deltaj=direction[i][1]
            idx_i=action[0]
            idx_j=action[1]
            while chessBoard[idx_i+deltai][idx_j+deltaj]==-1:
                chessBoard[idx_i+deltai][idx_j+deltaj]=1
                idx_i+=deltai
                idx_j+=deltaj
        if self.isGameOver():
            if self.get_score()*self.blackOrWhite>0:
                reward=1
            if self.get_score()*self.blackOrWhite<0:
                reward=-1
        else:
            reward=0
        if realy:
            self.chessBoard=chessBoard*self.blackOrWhite
            
            self.blackOrWhite=-self.blackOrWhite
            if not self.find_action_space():
                self.blackOrWhite=-self.blackOrWhite
            return self.chessBoard,reward,self.isGameOver()
        else:
            return chessBoard*self.blackOrWhite
    
    def get_score(self):
        return np.count_nonzero(self.chessBoard==1)-np.count_nonzero(self.chessBoard==-1)
    
    def randomAImove(self):
        action=choice(self.find_action_space())
        return self.take_action(action)
        


#
#episode=1000;
#scoreWhite=0;
#for i in range(episode):
#    A=BlackAndWhite()
#    isGameOver=False
#    while not isGameOver:
#        actionSpace=A.find_action_space()
#        action=choice(actionSpace)
#        isGameOver=A.take_action(action)
#        score=A.get_score()
#    print(score)
#    #    print(actionSpace)
#    #    print(action)
#    #    print(A.chessBoard)
#    if score>0:
#        scoreWhite+=1
#print('White win %d times'%scoreWhite)
#window=tk.Tk()
#window.mainloop()