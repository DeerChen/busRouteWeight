'''
@Description: 主函数
@Author: Senkita
@Date: 2020-05-06 11:58:07
@LastEditors: Senkita
@LastEditTime: 2020-05-06 12:36:28
'''
import pandas as pd
import json
from Calculate import DoubleDict, SQLQuery


def file2df(filePath):
    '''
    @description: 将公交站点信息.csv转为数据帧
    @param {str} 文件路径 
    @return: 保留单方向线路
    @author: Senkita
    '''
    file = pd.read_csv(filePath, encoding='gbk')
    sigleDirectionFile = file[file['方向'] == 1]
    return sigleDirectionFile


def nodeWeight(df):
    '''
    @description: 计算节点权重
    @param {DataFrame} 数据帧
    @return: 节点权重，公交车集合
    @author: Senkita
    '''
    stopWeight = dict(df['站点名称'].value_counts())
    for i in stopWeight:
        stopWeight[i] = int(stopWeight[i])

    busSet = set(df['线路名称'].tolist())
    return stopWeight, busSet


def save2json(dictContent, fileName):
    '''
    @description: 将字典数据保存为JSON格式
    @param {dict, str} 字典类型数据，文件名
    @return: 
    @author: Senkita
    '''
    jsonContent = json.dumps(dictContent, ensure_ascii=False)

    with open('./src/{}.json'.format(fileName), 'w', encoding='utf-8')as f:
        f.write(jsonContent)


def DoubleDictFun(df, busSet, stopWeight):
    '''
    @description: 双层字典
    @param {DataFrame, set, dict} 数据帧，公交车集合，节点权重
    @return: 节点总权重，边双重字典
    @author: Senkita
    '''
    d = DoubleDict(df, busSet, stopWeight)
    routeDict = d.edgeWeight()
    nodeTotalWeight = d.nodeTotalWeight()
    return nodeTotalWeight, routeDict


def SQLFun(databasePath, df, busSet, stopWeight):
    '''
    @description: 数据库
    @param {str, DataFrame, set, dict} 数据库路径，数据帧，公交车集合，节点权重 
    @return: 节点总权重，线路权重
    @author: Senkita
    '''
    sql = SQLQuery(databasePath)
    # sql.createTable()
    # sql.insertData(df, busSet)
    nodeTotalWeight = sql.nodeTotalWeight(stopWeight)
    edgeWeight = sql.edgeWeight()
    del sql
    return nodeTotalWeight, edgeWeight


def main():
    '''
    @description: 主函数入口
    @param {type} 
    @return: 
    @author: Senkita
    '''
    filePath = '公交站点信息.csv'
    df = file2df(filePath)
    stopWeight, busSet = nodeWeight(df)
    save2json(stopWeight, 'stopWeight')

    nodeTotalWeight, routeDict = DoubleDictFun(df, busSet, stopWeight)
    save2json(nodeTotalWeight, 'nodeTotalWeight')
    save2json(routeDict, 'routeDict')

    # databasePath = './src/edgeWeight.db'
    # nodeTotalWeightSQL, edgeWeight = SQLFun(databasePath, df, busSet, stopWeight)
    # save2json(nodeTotalWeightSQL, 'nodeTotalWeightSQL')
    # save2json(edgeWeight, 'edgeWeight')


if __name__ == "__main__":
    main()
