'''
@Description: 数据库实现
@Author: Senkita
@Date: 2020-05-06 11:58:41
@LastEditors: Senkita
@LastEditTime: 2020-05-06 12:39:01
'''
import sqlite3


class SQLQuery:
    def __init__(self, databasePath):
        self.conn = sqlite3.connect(databasePath)
        self.cursor = self.conn.cursor()
        self.prevStopResult, self.nextStopResult = self.nodeWeightQuery()
        self.edgeWeightResult = self.edgeWeightQuery()

    def createTable(self):
        '''
        @description: 创建表
        @param {type} 
        @return: 
        @author: Senkita
        '''
        self.cursor.execute(
            '''
            create table if not exists edgeWeight (
                id integer primary key not null,
                prevStop text not null,
                nextStop text not null,
                edgeWeight integer not null default 1
            );
            '''
        )
        self.conn.commit()

        self.cursor.execute('delete from edgeWeight;')
        self.conn.commit()

    def insertData(self, df, busSet):
        '''
        @description: 插入记录
        @param {DataFrame, set} 数据帧，公交车集合 
        @return: 
        @author: Senkita
        '''
        for busName in busSet:
            busRoute = df[df['线路名称'] == busName]
            busStop = busRoute['站点名称'].tolist()
            for i in range(1, len(busStop)):
                prevStop = busStop[i-1]
                nextStop = busStop[i]
                self.cursor.execute(
                    '''
                    insert into edgeWeight (
                        prevStop, nextStop
                    ) values ("{}", "{}");
                    '''.format(prevStop, nextStop)
                )
                self.conn.commit()

    def nodeWeightQuery(self):
        '''
        @description: 分组查询途径站点线路
        @param {type} 
        @return: SQL查询结果
        @author: Senkita
        '''
        self.cursor.execute(
            '''
            select prevStop, sum(edgeWeight) from edgeWeight group by prevStop;
            '''
        )
        prevStopResult = self.cursor.fetchall()

        self.cursor.execute(
            '''
            select nextStop, sum(edgeWeight) from edgeWeight group by nextStop;
            '''
        )
        nextStopResult = self.cursor.fetchall()
        return prevStopResult, nextStopResult

    def nodeTotalWeight(self, stopWeight):
        '''
        @description: 计算节点总权重
        @param {dict} 节点权重
        @return: 节点总权重
        @author: Senkita
        '''
        nodeTotalWeight = stopWeight.copy()
        for row in self.prevStopResult:
            nodeTotalWeight[row[0]] += row[1]
        for row in self.nextStopResult:
            nodeTotalWeight[row[0]] += row[1]
        return nodeTotalWeight

    def edgeWeightQuery(self):
        '''
        @description: 查询线路权重
        @param {type} 
        @return: SQL查询结果
        @author: Senkita
        '''
        self.cursor.execute(
            '''
            select prevStop, nextStop, sum(edgeWeight) from	edgeWeight group by prevStop, nextStop;
            '''
        )
        edgeWeightResult = self.cursor.fetchall()
        return edgeWeightResult

    def edgeWeight(self):
        '''
        @description: 格式化输出线路权重
        @param {type} 
        @return: 线路权重字典
        @author: Senkita
        '''
        routeDict = {}
        for row in self.edgeWeightResult:
            route = '{}-{}'.format(row[0], row[1])
            routeDict[route] = row[2]
        return routeDict

    def __del__(self):
        self.conn.close()
