#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/bin/env/python3
# Tools to find sgRNA or DNA sequence
# Author: Moqiqin
# Date: 2022.02.02


# In[ ]:


import re


# In[ ]:


def reverseDNA(dna):
    '''从5到3端输入一串DNA，返回其互补链(5`-3`)'''
    #a = list(dna)
    reversedDNA = ''
    dna=dna.upper().strip() #全部转为大写，并去除空格之类。
    b = ''.join(reversed(dna)) #先将整个DNA反转顺序，再一一与互补碱基对应
    for i in b:
        if i == "A":
            j = "T"
        elif i == "T":
            j = "A"
        elif i == "C":
            j = "G"
        elif i == "G":
            j = "C"
        else:
            j = "N"

        reversedDNA = reversedDNA + j
    return  reversedDNA


def getDNAPattern(pattern = "NGG"):
    """支持以下简并碱基，输入一段含有简并碱基的序列，输出正则表达式匹配规则文本。
    B = ['C','G','T']
    D = ['A','G','T']
    H = ['A','C','T']
    K = ['G','T']
    M = ['A','C']
    N = ['A','C','G','T']
    R = ['A','G']
    S = ['C','G']
    V = ['A','C','G']
    W = ['A','T']
    Y = ['C','T']
    """
    
    pattern = pattern.upper().strip()
    
    #将简并碱基转变为正则表达式pattern文本
    pattern =  re.sub("B","[C|G|T]",pattern)
    pattern =  re.sub("D","[A|G|T]",pattern)
    pattern =  re.sub("H","[A|C|T]",pattern)
    pattern =  re.sub("K","[G|T]",pattern)
    pattern =  re.sub("M","[A|C]",pattern)
    pattern =  re.sub("N","[A|C|G|T]",pattern)
    pattern =  re.sub("R","[A|G]",pattern)
    pattern =  re.sub("S","[C|G]",pattern)
    pattern =  re.sub("V","[A|C|G]",pattern)
    pattern =  re.sub("W","[A|T]",pattern)
    pattern =  re.sub("Y","[C|T]",pattern)
    #print(pattern)
    #pattern = re.compile(pattern)（不直接编译，因为后续可能还要添加规则。）
    return pattern


# In[211]:


class DNA:
    def __init__(self,dna):
        self.sequence = dna.upper().strip() #尽量全部大写，以免发生意外。
    
    
    def getSgRNA(self,pam="NGG",direction=0,spacerLength=20,repeatNum=4):
        pam = pam.upper().strip()
        direction = int(direction)
        spacerLength = int(spacerLength) 
        repeatNum = int(repeatNum)#初始化参数
        
        
        if direction: #即PAM-SPACER
            pattern = getDNAPattern(pam) + spacerLength*"."
            
        else: #即SPACER-PAM
            pattern =  spacerLength*"." + getDNAPattern(pam)
            
        self.sgRNAiterP = re.finditer(pattern,self.sequence)
        self.sgRNAiterM = re.finditer(pattern,reverseDNA(self.sequence))
        
        
        sgRNAList = {}
        repeatList = {}
        nonRepeatLis = {}
        
        while True:
            try:
                sgInfo = next(self.sgRNAiterP)
                location = sgInfo.span()
                
                if direction:#pam spacer
                    sgRNA = sgInfo.group()[len(pam):]
                else:
                    sgRNA = sgInfo.group()[:-len(pam)]
                    
                
                #print(sgRNA)
                #print(sgRNAList.keys())
                if sgRNA in sgRNAList.keys():
                    #print(sgRNA)
                    sgRNAList[sgRNA].append([location,"+"])
                else:
                    #print('bb')
                    #print(sgRNA)
                    sgRNAList[sgRNA] = [[location,"+"]]
                    
            except:
                break
                
        while True:
            try:
                sgInfo = next(self.sgRNAiterM)
                location = sgInfo.span()
                
                if direction:#pam spacer
                    sgRNA = sgInfo.group()[len(pam):]
                else:
                    sgRNA = sgInfo.group()[:-len(pam)]
                    
                
                #print(sgRNA)
                #print(sgRNAList.keys())
                if sgRNA in sgRNAList.keys():
                    #print(sgRNA)
                    sgRNAList[sgRNA].append([location,"-"])
                else:
                    #print('bb')
                    #print(sgRNA)
                    sgRNAList[sgRNA] = [[location,"-"]]
                    
            except:
                break
            
        for i in sgRNAList:
            if len(sgRNAList[i]) > repeatNum:
                repeatList[i] = [len(sgRNAList[i]),sgRNAList[i]]
            elif len(sgRNAList[i]) < 2:
                nonRepeatLis[i] = [len(sgRNAList[i]),sgRNAList[i]]
            
        self.sgRNAList = sgRNAList
        self.nonRepeatSgRNAList = nonRepeatLis
        self.repeatSgRNAList = repeatList
        return sgRNAList
    
    def getRepeatSg(self,pam="NGG",direction=0,spacerLength=20,repeatNum=4):
        pam = pam.upper().strip()
        direction = int(direction)
        spacerLength = int(spacerLength) 
        repeatNum = int(repeatNum)#初始化参数
        self.getSgRNA(pam,direction,spacerLength,repeatNum)
        return self.repeatSgRNAList
        
    def getNonRepeatSg(self,pam="NGG",direction=0,spacerLength=20,repeatNum=4):
        pam = pam.upper().strip()
        direction = int(direction)
        spacerLength = int(spacerLength) 
        repeatNum = int(repeatNum)#初始化参数
        self.getSgRNA(pam,direction,spacerLength,repeatNum)
        return self.nonRepeatSgRNAList
    
    def indexSequence(self,pattern):
        pattern = pattern.upper().strip()
        pattern = getDNAPattern(pattern)
        result = re.finditer(pattern, self.sequence)
        return result

