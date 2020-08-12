'''
Description: 北京公交线路节点权重计算
Author: Senkita
Date: 2020-07-13 13:44:49
LastEditors: Senkita
LastEditTime: 2020-08-12 16:39:35
'''

import pandas as pd
import re
import json
import matplotlib.pyplot as plt


def data_cleaning(dirty_read_file_path, clean_read_file_path):
    '''
    description: 对new.txt中的脏数据进行清洗
    param {str} [dirty_read_file_path] - 脏数据文件路径
    return {type}
    author: Senkita
    '''
    # * 读取脏数据
    dirty_read = ''

    with open(dirty_read_file_path, 'r', encoding='utf-8') as f:
        txt = f.readlines()
        for i in txt:
            dirty_read += i

    # * 将脏数据中非数字非中文部分剔除
    clean_read = re.sub(r'[^\w\u4e00-\u9fff]+', ' ', dirty_read)

    # * 拆分词组
    clean_read_list = clean_read.split(' ')

    # * 重新按线路分行
    bus_pattern = re.compile(r'\d')

    new_doc = ''

    for i in range(len(clean_read_list)):
        if re.findall(bus_pattern, clean_read_list[i]) != []:
            new_doc += '\n'
        new_doc += clean_read_list[i]
        new_doc += ' '

    # * 将清洗完的数据写入新文档
    with open(clean_read_file_path, 'w', encoding='utf-8') as f:
        f.write(new_doc)


def txt2df(clean_read_file_path, excel_file_path):
    '''
    description: 将数据转成数据帧方便后续处理,并存为Excel备份
    param {str} [clean_read_file_path] - 数据文件路径
          {str} [excel_file_name] - excel文件路径
    return {DataFrame} [df] - 线路数据帧
    author: Senkita
    '''
    df = pd.DataFrame(columns=['bus', 'stop'])

    row = 0

    with open(clean_read_file_path, 'r', encoding='utf-8') as f:
        route = f.readline()
        while route:
            # * 行第一项为车路
            bus = route.split(' ')[0]
            # * 行其余项为站点
            # * 顺道去一下行尾空行
            stop_list = route.rstrip().split(' ')[1:]
            for stop in stop_list:
                df.loc[row, 'bus'] = bus
                df.loc[row, 'stop'] = stop
                row += 1
            route = f.readline()

    # * 仅作备份
    # df.to_excel(excel_file_path, index=False, encoding='utf-8')

    # * 数据帧部分直接导出,继续操作
    return df


def construct_route_dict(df):
    '''
    @description: 构建线路字典
    @param {DataFrame} [df] - 线路数据帧
    @return: {dict} [route_dict] - 线路字典
    @author: Senkita
    '''
    # * 车路集合
    bus_set = set(df['bus'].tolist())

    route_dict = {}
    for bus in bus_set:
        # * 依车寻路
        route = df[df['bus'] == bus]
        stop = route['stop'].tolist()
        for i in range(1, len(stop)):
            prev_stop = stop[i - 1]
            next_stop = stop[i]
            if prev_stop in route_dict:
                if next_stop in route_dict[prev_stop]:
                    route_dict[prev_stop][next_stop] += 1
                else:
                    route_dict[prev_stop][next_stop] = 1
            else:
                route_dict[prev_stop] = {next_stop: 1}
    return route_dict


def compute_node_weight(route_dict):
    '''
    description: 计算节点总权重,节点总权重=经过节点边的权重
    param {dict} [route_dict] - 线路字典
    return {dict} [node_weight] - 节点总权重
    author: Senkita
    '''
    node_weight = {}

    # * 求节点作为前站的边权重
    for prev_stop in route_dict:
        prev_stop_value_list = [
            route_dict[prev_stop][key] for key in route_dict[prev_stop]
        ]
        prev_stop_edge_weight = value_list_sum(prev_stop_value_list)
        if prev_stop in node_weight:
            node_weight[prev_stop] += prev_stop_edge_weight
        else:
            node_weight[prev_stop] = 1

        # * 再加上节点作为后站的边权重
        for next_stop in route_dict[prev_stop]:
            if next_stop in node_weight:
                node_weight[next_stop] += route_dict[prev_stop][next_stop]
            else:
                node_weight[next_stop] = 1

    return node_weight


def value_list_sum(value_list):
    '''
    @description: 计算列表中值总和
    @param {list} [value_list] - 值列表
    @return: {int} [sum] - 值总和
    @author: Senkita
    '''
    value_list_sum = 0
    for value in value_list:
        value_list_sum += value
    return value_list_sum


def save2json(dict_content, file_name):
    '''
    description: 将字典数据转化为JSON文件备份
    param {dict} [dict_content] - 字典数据
          {str} [file_name] - 文件名
    return {type}
    author: Senkita
    '''
    json_content = json.dumps(dict_content, ensure_ascii=False)
    with open('{}.json'.format(file_name), 'w', encoding='utf-8') as f:
        f.write(json_content)


def distinguish_odd_even(node_weight):
    '''
    description: 分出节点总权重奇偶
    param {dict} [node_weight] - 节点总权重
    return {DataFrame} [df_even] - 权重为偶的数据帧
           {DataFrame} [df_odd] - 权重为奇的数据帧
    author: Senkita
    '''
    df_weight = pd.DataFrame(columns=['weight'])

    row = 0
    for v in node_weight.values():
        df_weight.loc[row, 'weight'] = int(v)
        row += 1

    weight_count = dict(df_weight['weight'].value_counts())

    df_even = pd.DataFrame(columns=['weight', 'count'])
    df_odd = pd.DataFrame(columns=['weight', 'count'])

    row_even = 0
    row_odd = 0

    for k, v in weight_count.items():
        if k % 2 == 0:
            df_even.loc[row_even, 'weight'] = k
            df_even.loc[row_even, 'count'] = v
            row_even += 1
        else:
            df_odd.loc[row_odd, 'weight'] = k
            df_odd.loc[row_odd, 'count'] = v
            row_odd += 1

    return df_even, df_odd


def draw(df_even, df_odd):
    '''
    description: 作图
    param {DataFrame} [df_even] - 权重为偶的数据帧
          {DataFrame} [df_odd] - 权重为奇的数据帧
    return {type}
    author: Senkita
    '''
    plt.figure()

    # * 偶数散点图
    weight_even = df_even['weight'].tolist()
    count_even = df_even['count'].tolist()
    even = plt.scatter(weight_even, count_even, c='r', marker='o')

    # * 奇数散点图
    weight_odd = df_odd['weight'].tolist()
    count_odd = df_odd['count'].tolist()
    odd = plt.scatter(weight_odd, count_odd, c='g', marker='*')

    # * 双对数坐标
    plt.loglog()

    plt.xlabel('Weight')
    plt.ylabel('Number of Bus Stops')

    plt.legend([even, odd], ['Even Weight', 'Odd Weight'], loc='upper right')
    plt.savefig('model.png')
    plt.show()


def main():
    dirty_read_file_path = 'new.txt'
    clean_read_file_path = 'cleanRead.txt'
    excel_file_path = 'Beijing.xlsx'

    data_cleaning(dirty_read_file_path, clean_read_file_path)

    df = txt2df(clean_read_file_path, excel_file_path)
    route_dict = construct_route_dict(df)
    node_weight = compute_node_weight(route_dict)
    # save2json(node_weight, 'node_weight')

    df_even, df_odd = distinguish_odd_even(node_weight)
    draw(df_even, df_odd)


if __name__ == "__main__":
    main()
