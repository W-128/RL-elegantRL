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
import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import random

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


def plot_waiting_time_and_require_time(success_request_list, waiting_time_index, rtl_index, plot_cfg, tag='train'):
    sns.set()
    fig = plt.figure()
    plt.title("more provision {} for {}".format(plot_cfg.algo_name, plot_cfg.env_name))
    plt.xlabel('success request')
    rtl_dic = {}
    for success_request in success_request_list:
        if success_request[rtl_index] not in rtl_dic:
            rtl_dic[success_request[rtl_index]] = []
            rtl_dic[success_request[rtl_index]].append(success_request[waiting_time_index])
        else:
            rtl_dic[success_request[rtl_index]].append(success_request[waiting_time_index])
    import random
    for rtl in rtl_dic:
        plt.plot(random.sample(rtl_dic[rtl], 100), label=rtl)
    plt.legend()
    if plot_cfg.save:
        plt.savefig(plot_cfg.result_path + "{}_more_provision".format(tag))
    plt.show()


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


def concurrent_request_num_per_second_list_to_concurrent_request_num(concurrent_request_num_per_second_list):
    import uuid
    import csv

    request_list = []
    rtl_and_request_id_list = []
    with open('../gatling-charts-highcharts-bundle-3.6.1/user-files/simulations/traffic.csv', 'w', newline='') as f:
        f_csv = csv.writer(f)
        for i in range(len(concurrent_request_num_per_second_list)):
            request_sum_the_second = concurrent_request_num_per_second_list[i]
            f_csv.writerow([request_sum_the_second])
            for j in range(request_sum_the_second):
                # [request_id, arrive_time, rtl]
                request = []
                request_id = str(uuid.uuid1())
                request.append(request_id)
                request.append(i)
                # request.append(np.random.choice(rtl_list))
                rtl_float = random.gauss(10, 1)
                rtl_int = int(rtl_float + 0.5)
                if rtl_int < 0:
                    rtl_int = 0
                if rtl_int > 20:
                    rtl_int = 20
                request.append(rtl_int)
                request_list.append(request)
                rtl_and_request_id_list.append([rtl_int, request_id])

    headers = ['request_id', 'arrive_time', 'rtl']
    with open('concurrent_request_num.csv', 'w', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(request_list)

    with open('../gatling-charts-highcharts-bundle-3.6.1/user-files/rtl_and_request_id.csv', 'w', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(['rtl', 'request_id'])
        f_csv.writerows(rtl_and_request_id_list)
