from torch import threshold


def test(cfg, env, agent):
    print('开始测试！')
    print(f'环境：{cfg.env_name}, 算法：{cfg.algo_name}')
    ep_reward = 0  # 记录每个episode的reward
    threshold=env.threshold
    # threshold=30
    if cfg.algo_name == 'fifo':
        active_request_group_by_remaining_time_list = env.reset_fifo()  # 重置环境, 重新开一局（即开始新的一个回合）
        while True:
            submit_request_id_list = agent.predict(active_request_group_by_remaining_time_list,
                                                   threshold)  # 根据算法选择一个动作
            next_active_request_group_by_remaining_time_list, reward, done, _ = env.step_fifo(
                submit_request_id_list)  # 与环境进行一个交互
            active_request_group_by_remaining_time_list = next_active_request_group_by_remaining_time_list  # 更新状态
            ep_reward += reward
            if done:
                break
    else:
        state = env.reset()  # 重置环境, 重新开一局（即开始新的一个回合）
        while True:
            action = agent.predict(state, threshold)  # 根据算法选择一个动作
            next_state, reward, done, _ = env.step(action)  # 与环境进行一个交互
            state = next_state  # 更新状态
            ep_reward += reward
            # print('action:' + str(action))
            if done:
                # env.save_success_request()
                break
    print('step:' + str(env.t))
    print('该回合奖励：' + str(ep_reward))
    print('sla违约率：{:.1f}%'.format(env.get_violation_rate() * 100))
    print('sla失败率：{:.1f}%'.format(env.get_fail_rate() * 100))
    print('超供均值：{:.1f}'.format(env.get_more_provision_mean()))
    print('超供面积比例：{:.1f}%'.format(env.get_over_prov_rate() * 100))
    print('每秒提交量方差：{:.1f}'.format(env.get_submit_request_num_per_second_variance()))
    print('提交量大于阈值的概率：{:.1f}%'.format(env.get_more_than_threshold_rate()))
    env.print_wait_time_avg()
    print('完成测试！')
    return env.get_success_request_dic_key_is_end_time_and_rtl_list()
