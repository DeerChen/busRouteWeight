'''
@Description: 双层字典实现
@Author: Senkita
@Date: 2020-05-06 11:57:50
@LastEditors: Senkita
@LastEditTime: 2020-05-06 12:41:07
'''
class DoubleDict:
    def __init__(self, df, busSet, stopWeight):
        self.df = df
        self.busSet = busSet
        self.stopWeight = stopWeight
        self.routeDict = self.edgeWeight()

    def edgeWeight(self):
        '''
        @description: 构建线路双层字典
        @param {type} 
        @return: 线路双层字典
        @author: Senkita
        '''
        routeDict = {}
        for busName in self.busSet:
            busRoute = self.df[self.df['线路名称'] == busName]
            busStop = busRoute['站点名称'].tolist()
            for i in range(1, len(busStop)):
                prevStop = busStop[i-1]
                nextStop = busStop[i]
                if prevStop in routeDict:
                    if nextStop in routeDict[prevStop]:
                        routeDict[prevStop][nextStop] += 1
                    else:
                        routeDict[prevStop][nextStop] = 1
                else:
                    routeDict[prevStop] = {
                        nextStop: 1
                    }
        return routeDict

    def nodeTotalWeight(self):
        '''
        @description: 节点总权重计算
        @param {type} 
        @return: 节点总权重字典
        @author: Senkita
        '''
        nodeTotalWeight = self.stopWeight.copy()
        for prevStop in self.routeDict:
            valueList = [self.routeDict[prevStop][key]
                         for key in self.routeDict[prevStop]]
            count = self.sum(valueList)
            nodeTotalWeight[prevStop] += count
            for nextStop in self.routeDict[prevStop]:
                nodeTotalWeight[nextStop] += self.routeDict[prevStop][nextStop]
        return nodeTotalWeight

    @staticmethod
    def sum(l):
        '''
        @description: 计算列表中值总和
        @param {list} 列表
        @return: 值总和
        @author: Senkita
        '''
        sum = 0
        for i in l:
            sum += i
        return sum
