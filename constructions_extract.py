import copy

def pformatStrDraw(pformatStr):
    from nltk import Tree
    nltkTree = Tree.fromstring(pformatStr)
    nltkTree.draw()


def pformatStr_2_bracketedTreeList(pformatStr):
    bracketedTreeStr=''.join(pformatStr.split())
    res=[]
    curNode = ''
    for c in bracketedTreeStr:
        if c == ')' or c == '(':
            if curNode:
                res.append(curNode)
                curNode = ''
            res.append(c)
        else:
            curNode += c
    return res


class pNode(object):
    def __init__(self,val):
        self.val=val
        self.child=list()
    def addChild(self,ci):
        self.child.append(ci)

from collections import deque

class pTree(object):
    def __init__(self,pformatStr):
        self.m_pformatStr=pformatStr
        self.m_sent=self.pformatStr_2_Sent()
        self.m_treeRoot=self.bracketedTreeList_2_tree()

    def Draw(self):
        from nltk import Tree
        nltkTree = Tree.fromstring(self.m_pformatStr)
        nltkTree.draw()

    def pformatStr_2_Sent(self):
        sent=''
        bracketedTreeStr = ''.join(self.m_pformatStr.split())
        for c in bracketedTreeStr:
            if c == '(' or c == ')' :
                pass
            else:
                sent+=c
        return sent


    def pformatStr_2_bracketedTreeList(self):
        bracketedTreeStr = ''.join(self.m_pformatStr.split())
        bracketedTreeList = []
        curNode = ''
        for c in bracketedTreeStr:
            if c == ')' or c == '(':
                if curNode:
                    bracketedTreeList.append(curNode)
                    curNode = ''
                bracketedTreeList.append(c)
            else:
                curNode += c
        return bracketedTreeList

    def bracketedTreeList_2_tree(self):
        # print('调用建树函数')
        st=deque()
        li=self.pformatStr_2_bracketedTreeList()
        for i in range(len(li) - 1):
            if li[i] == '(':
                pass
            elif li[i] == ')':
                p = st.pop()
                st[-1].addChild(p)
                # p是根节点
            else:
                st.append(pNode(li[i]))
        return st[-1]

    # 使用非递归的先序遍历打印树
    def Print(self):
        st=deque()
        st.append(self.m_treeRoot)
        while st:
            curNode=st.pop()
            if curNode.child:
                print(curNode.val,[child.val for child in curNode.child])
            for i in range(len(curNode.child)-1,-1,-1):
                st.append((curNode.child)[i])

    def getRoot(self):
       return self.m_treeRoot

    def getSent(self):
        return self.m_sent

def getLeafStr(root, leafLi):
    if root:
        if not root.child:
            leafLi.append(root.val)
        for ch in root.child:
            getLeafStr(ch, leafLi)

def getTreeDepth(root):
    if not root:
        return 0
    res = 0
    for chi in root.child:
        res = max(res,getTreeDepth(chi))
    return res+1


def extract_produce(root,par,res):
	if root:
		if root.val in ['DER得'] :
			chi_val = [chi.val for chi in par.child]

			# chi_val[0] = chi_val[0][0:2]
			# if chi_val[2][0:2] == 'VV':
			# 	chi_val[2] = 'VV'
			res.append(par.val+' -> '+'+'.join(chi_val))
			# if par.val !=  'VP':
			# 	leafLi = []
			# 	getLeafStr(par, leafLi)
			# 	print(leafLi)
		for chi in root.child:
			extract_produce(chi, root, res)