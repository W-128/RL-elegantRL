#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2021-03-12 16:02:24
LastEditor: John
LastEditTime: 2021-11-30 18:39:19
Discription:
Environment:
'''
from cProfile import label
import os
from statistics import mean
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import random
import math
from matplotlib.font_manager import FontProperties  # 导入字体模块

import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def chinese_font():
    ''' 设置中文字体，注意需要根据自己电脑情况更改字体路径，否则还是默认的字体
    '''
    try:
        font = FontProperties(fname='/System/Library/Fonts/STHeiti Light.ttc', size=15)  # fname系统字体路径，此处是mac的
    except:
        font = None
    return font


def plot_rewards_cn(rewards, ma_rewards, plot_cfg, tag='train'):
    ''' 中文画图
    '''
    sns.set()
    plt.figure()
    plt.title(u"{}环境下{}算法的学习曲线".format(plot_cfg.env_name, plot_cfg.algo_name), fontproperties=chinese_font())
    plt.xlabel(u'回合数', fontproperties=chinese_font())
    plt.plot(rewards)
    plt.plot(ma_rewards)
    plt.legend((
        u'奖励',
        u'滑动平均奖励',
    ), loc="best", prop=chinese_font())
    if plot_cfg.save:
        plt.savefig(plot_cfg.result_path + f"{tag}_rewards_curve_cn")
    # plt.show()


def plot_rewards(rewards, ma_rewards, plot_cfg, tag='train'):
    sns.set()
    plt.figure()  # 创建一个图形实例，方便同时多画几个图
    plt.title("learning curve on {} of {} for {}".format(plot_cfg.device, plot_cfg.algo_name, plot_cfg.env_name))
    plt.xlabel('epsiodes')
    plt.plot(rewards, label='rewards')
    plt.plot(ma_rewards, label='ma rewards')
    plt.legend()
    if plot_cfg.save:
        plt.savefig(plot_cfg.result_path + "{}_rewards_curve".format(tag))
    plt.show()


def plot_success_rate(success_rate, plot_cfg, tag='train'):
    sns.set()
    plt.figure()  # 创建一个图形实例，方便同时多画几个图
    plt.title("learning curve on {} of {} for {}".format(plot_cfg.device, plot_cfg.algo_name, plot_cfg.env_name))
    plt.xlabel('epsiodes')
    plt.plot(success_rate, label='success rate')
    plt.legend()
    if plot_cfg.save:
        plt.savefig(plot_cfg.result_path + "{}_success_curve".format(tag))
    plt.show()


def plot_waiting_time_and_require_time(success_request_dic_key_is_end_time, rtl_list, plot_cfg, tag='train'):
    sns.set()
    fig = plt.figure()
    plt.title("more provision {} for {}".format(plot_cfg.algo_name, plot_cfg.env_name))
    plt.xlabel('time(second)')
    x = list(success_request_dic_key_is_end_time.keys())
    rtl_avg_wait_time_dic = {}
    # {rtl1:[],rtl2:[]}
    for rtl in rtl_list:
        rtl_avg_wait_time_dic[rtl] = []
    for end_time in success_request_dic_key_is_end_time.keys():
        rtl_wait_time_dic = {}
        # {rtl1:[],rtl2:[]}
        for rtl in rtl_list:
            rtl_wait_time_dic[rtl] = []
        for request in success_request_dic_key_is_end_time[end_time]:
            rtl_wait_time_dic[request['rtl']].append(request['wait_time'])
        for rtl in rtl_wait_time_dic:
            if rtl_wait_time_dic[rtl] == []:
                rtl_avg_wait_time_dic[rtl].append(np.nan)
            else:
                rtl_avg_wait_time_dic[rtl].append(np.mean(rtl_wait_time_dic[rtl]))

    for rtl in rtl_list:
        mask = np.isfinite(rtl_avg_wait_time_dic[rtl])
        line, = plt.plot(np.array(x)[mask], np.array(rtl_avg_wait_time_dic[rtl])[mask], ls="--", lw=1)
        plt.plot(x, rtl_avg_wait_time_dic[rtl], color=line.get_color(), lw=1.5, label=rtl)
        # 辅助线
        sup_line = [rtl for i in range(len(x))]
        plt.plot(x, sup_line, color='black', linestyle='--', linewidth='1')
    plt.legend()
    if plot_cfg.save:
        plt.savefig(plot_cfg.result_path + "{}_more_provision".format(tag))
    # plt.show()


def plot_losses(losses, algo="DQN", save=True, path='./'):
    sns.set()
    plt.title("loss curve of {}".format(algo))
    plt.xlabel('epsiodes')
    plt.plot(losses, label='rewards')
    plt.legend()
    if save:
        plt.savefig(path + "losses_curve")
    plt.show()


def save_results(rewards, ma_rewards, tag='train', path='./results'):
    ''' 保存奖励
    '''
    np.save(path + '{}_rewards.npy'.format(tag), rewards)
    np.save(path + '{}_ma_rewards.npy'.format(tag), ma_rewards)
    print('结果保存完毕！')


def save_success_rate(success_rate, tag='train', path='./results'):
    '''
    保存成功率
    '''
    np.save(path + '{}_success_rate.npy'.format(tag), success_rate)
    print('成功率保存完毕！')


def make_dir(*paths):
    ''' 创建文件夹
    '''
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def del_empty_dir(*paths):
    ''' 删除目录下所有空文件夹
    '''
    for path in paths:
        dirs = os.listdir(path)
        for dir in dirs:
            if not os.listdir(os.path.join(path, dir)):
                os.removedirs(os.path.join(path, dir))


def generate_next_request(success_request, task_num):
    if task_num == 2:
        # request={'request_id', 'arrive_time', 'rtl', 'task_id', 'remaining_time'}
        # success_request{'request_id', 'arrive_time', 'rtl', 'task_id', 'wait_time'}
        if success_request['task_id'] == 'task1':
            arrive_time = success_request['wait_time'] + success_request['arrive_time'] + 3
            rtl = success_request['rtl']
            request = {}
            request['request_id'] = success_request['request_id'] + '-1'
            request['arrive_time'] = arrive_time
            request['rtl'] = rtl
            request['task_id'] = 'task2'
            return request
    return {}


def concurrent_request_num_per_second_list_to_concurrent_request_num(concurrent_request_num_per_second_list):
    import uuid
    import csv
    rtl_dic = {'2': 0.1, '7': 0.9}

    request_list = []
    for i in range(len(concurrent_request_num_per_second_list)):
        request_sum_the_second = concurrent_request_num_per_second_list[i]
        rtl_request_num_dic = {}
        used_request_sum_the_second = 0
        for rtl in rtl_dic:
            rtl_request_num = math.floor(request_sum_the_second * rtl_dic[rtl])
            rtl_request_num_dic[rtl] = rtl_request_num
            used_request_sum_the_second += rtl_request_num
        if used_request_sum_the_second < request_sum_the_second:
            rtl_request_num_dic['7'] += request_sum_the_second - used_request_sum_the_second
        for rtl in rtl_request_num_dic:
            for j in range(rtl_request_num_dic[rtl]):
                # [request_id, arrive_time, rtl]
                request = []
                request.append(str(uuid.uuid1()))
                request.append(i)
                request.append(rtl)
                request_list.append(request)

    headers = ['request_id', 'arrive_time', 'rtl']
    with open('concurrent_request_num.csv', 'w', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(request_list)
