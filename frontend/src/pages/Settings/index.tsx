import React, { useState } from 'react';
import { Card, Form, Input, Switch, Button, message, Tabs, Divider, Space } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import axios from 'axios';
import type { SystemConfig } from '../../types';

const Settings: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [configs, setConfigs] = useState<Record<string, any>>({});
  const [form] = Form.useForm();
  const [aiForm] = Form.useForm();
  const [botForm] = Form.useForm();

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.get('/api/config', {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      const configMap: Record<string, any> = {};
      response.data.items.forEach((item: SystemConfig) => {
        configMap[item.key] = item.value;
      });
      setConfigs(configMap);

      if (configMap.whitelist) {
        form.setFieldsValue(configMap.whitelist);
      }
      if (configMap.ai) {
        aiForm.setFieldsValue(configMap.ai);
      }
      if (configMap.bot) {
        botForm.setFieldsValue(configMap.bot);
      }
    } catch (error) {
      message.error('获取配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleWhitelistSave = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.put(
        '/api/config/whitelist',
        { value: form.getFieldsValue() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleAISave = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.put(
        '/api/config/ai',
        { value: aiForm.getFieldsValue() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleBotSave = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.put(
        '/api/config/bot',
        { value: botForm.getFieldsValue() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  const tabItems = [
    {
      key: 'whitelist',
      label: '白名单配置',
      children: (
        <Form form={form} layout="vertical">
          <Form.Item name="enable_whitelist" label="启用白名单机制" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="welcome_msg" label="白名单用户欢迎语">
            <Input.TextArea rows={3} placeholder="欢迎使用微信机器人！" />
          </Form.Item>
          <Form.Item name="reject_msg" label="非白名单用户拒绝提示">
            <Input.TextArea rows={2} placeholder="您暂无权限使用此功能，请联系管理员添加白名单。" />
          </Form.Item>
          <Button type="primary" icon={<SaveOutlined />} onClick={handleWhitelistSave}>
            保存配置
          </Button>
        </Form>
      ),
    },
    {
      key: 'ai',
      label: 'AI模型配置',
      children: (
        <Form form={aiForm} layout="vertical">
          <Form.Item name="model" label="模型名称">
            <Input defaultValue="deepseek-chat" disabled />
          </Form.Item>
          <Form.Item name="temperature" label="温度参数" extra="控制回复的随机性，0-1之间，越低越确定">
            <Input type="number" min={0} max={1} step={0.1} defaultValue={0.7} />
          </Form.Item>
          <Form.Item name="max_tokens" label="最大Token数" extra="单次回复的最大长度">
            <Input type="number" min={100} max={4000} defaultValue={2000} />
          </Form.Item>
          <Button type="primary" icon={<SaveOutlined />} onClick={handleAISave}>
            保存配置
          </Button>
        </Form>
      ),
    },
    {
      key: 'bot',
      label: '机器人基础配置',
      children: (
        <Form form={botForm} layout="vertical">
          <Form.Item name="name" label="机器人名称">
            <Input placeholder="微信助手" />
          </Form.Item>
          <Form.Item name="sleep_enabled" label="启用休眠时段" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Space>
            <Form.Item name="sleep_start" label="休眠开始" noStyle>
              <Input placeholder="23:00" style={{ width: 120 }} />
            </Form.Item>
            <span style={{ lineHeight: '32px' }}>至</span>
            <Form.Item name="sleep_end" label="休眠结束" noStyle>
              <Input placeholder="07:00" style={{ width: 120 }} />
            </Form.Item>
          </Space>
          <Button type="primary" icon={<SaveOutlined />} onClick={handleBotSave}>
            保存配置
          </Button>
        </Form>
      ),
    },
  ];

  return (
    <div className="fade-in">
      <h1 style={{ marginBottom: 24 }}>系统配置</h1>
      <Tabs items={tabItems} />
    </div>
  );
};

export default Settings;
