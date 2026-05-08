import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  Modal,
  Form,
  message,
  Popconfirm,
  Switch,
  Select,
  Drawer,
  Descriptions,
  Divider,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  MessageOutlined,
} from '@ant-design/icons';
import { useEffect } from 'react';
import { groupsApi } from '../../api/groups';
import type { BotGroup } from '../../types';
import dayjs from 'dayjs';

const Groups: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [groups, setGroups] = useState<BotGroup[]>([]);
  const [pagination, setPagination] = useState({ total: 0, page: 1, pageSize: 20 });
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState<BotGroup | null>(null);
  const [isWelcomeOpen, setIsWelcomeOpen] = useState(false);
  const [isAIOpen, setIsAIOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<BotGroup | null>(null);
  const [form] = Form.useForm();
  const [welcomeForm] = Form.useForm();
  const [aiForm] = Form.useForm();

  useEffect(() => {
    fetchData();
  }, [pagination.page, pagination.pageSize, searchKeyword]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await groupsApi.getList({
        page: pagination.page,
        page_size: pagination.pageSize,
        keyword: searchKeyword || undefined,
      });
      setGroups(result.items);
      setPagination((prev) => ({ ...prev, total: result.total }));
    } catch (error) {
      message.error('获取群组列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingGroup(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (record: BotGroup) => {
    setEditingGroup(record);
    form.setFieldsValue({
      room_id: record.room_id,
      room_name: record.room_name,
      owner_id: record.owner_id,
      owner_name: record.owner_name,
    });
    setIsModalOpen(true);
  };

  const handleView = (record: BotGroup) => {
    setSelectedGroup(record);
  };

  const handleDelete = async (id: number) => {
    try {
      await groupsApi.delete(id);
      message.success('删除成功');
      fetchData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingGroup) {
        await groupsApi.update(editingGroup.id, values);
        message.success('更新成功');
      } else {
        await groupsApi.create(values);
        message.success('添加成功');
      }
      setIsModalOpen(false);
      fetchData();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleWelcomeEdit = (record: BotGroup) => {
    setSelectedGroup(record);
    welcomeForm.setFieldsValue({
      welcome_enabled: record.welcome_enabled,
      welcome_message: record.welcome_message,
    });
    setIsWelcomeOpen(true);
  };

  const handleWelcomeSubmit = async () => {
    try {
      const values = await welcomeForm.validateFields();
      await groupsApi.updateWelcome(selectedGroup!.id, values);
      message.success('更新成功');
      setIsWelcomeOpen(false);
      fetchData();
    } catch (error) {
      message.error('更新失败');
    }
  };

  const handleAIEdit = (record: BotGroup) => {
    setSelectedGroup(record);
    aiForm.setFieldsValue({
      ai_enabled: record.ai_enabled,
      ai_sleep_start: record.ai_sleep_start,
      ai_sleep_end: record.ai_sleep_end,
    });
    setIsAIOpen(true);
  };

  const handleAISubmit = async () => {
    try {
      const values = await aiForm.validateFields();
      await groupsApi.updateAI(selectedGroup!.id, values);
      message.success('更新成功');
      setIsAIOpen(false);
      fetchData();
    } catch (error) {
      message.error('更新失败');
    }
  };

  const columns = [
    {
      title: '群ID',
      dataIndex: 'room_id',
      key: 'room_id',
      width: 180,
      ellipsis: true,
    },
    {
      title: '群名称',
      dataIndex: 'room_name',
      key: 'room_name',
      width: 150,
    },
    {
      title: '群主',
      dataIndex: 'owner_name',
      key: 'owner_name',
      width: 100,
      render: (text: string) => text || '-',
    },
    {
      title: '消息数',
      dataIndex: 'message_count',
      key: 'message_count',
      width: 100,
      render: (count: number) => count || 0,
    },
    {
      title: '欢迎语',
      dataIndex: 'welcome_enabled',
      key: 'welcome_enabled',
      width: 100,
      render: (enabled: boolean) => (
        <Tag color={enabled ? 'green' : 'default'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: 'AI对话',
      dataIndex: 'ai_enabled',
      key: 'ai_enabled',
      width: 100,
      render: (enabled: boolean) => (
        <Tag color={enabled ? 'blue' : 'default'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '最后活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 170,
      render: (text: string) =>
        text ? dayjs(text).format('YYYY-MM-DD HH:mm') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: BotGroup) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => handleWelcomeEdit(record)}>
            欢迎语
          </Button>
          <Button type="link" size="small" onClick={() => handleAIEdit(record)}>
            AI配置
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm
            title="确认删除?"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>群组管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          添加群组
        </Button>
      </div>

      <div className="table-filters">
        <Input.Search
          placeholder="搜索群ID或群名称"
          allowClear
          style={{ width: 300 }}
          prefix={<SearchOutlined />}
          onSearch={(value) => {
            setSearchKeyword(value);
            setPagination((prev) => ({ ...prev, page: 1 }));
          }}
        />
      </div>

      <Table
        columns={columns}
        dataSource={groups}
        rowKey="id"
        loading={loading}
        pagination={{
          current: pagination.page,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPagination({ ...pagination, page, pageSize });
          },
        }}
      />

      <Modal
        title={editingGroup ? '编辑群组' : '添加群组'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => setIsModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="room_id"
            label="群ID (Room ID)"
            rules={[{ required: true, message: '请输入群ID' }]}
          >
            <Input placeholder="请输入群ID" disabled={!!editingGroup} />
          </Form.Item>
          <Form.Item name="room_name" label="群名称">
            <Input placeholder="请输入群名称（可选）" />
          </Form.Item>
          <Form.Item name="owner_id" label="群主ID">
            <Input placeholder="请输入群主ID（可选）" />
          </Form.Item>
          <Form.Item name="owner_name" label="群主昵称">
            <Input placeholder="请输入群主昵称（可选）" />
          </Form.Item>
        </Form>
      </Modal>

      <Drawer
        title="欢迎语配置"
        open={isWelcomeOpen}
        onClose={() => setIsWelcomeOpen(false)}
        onOk={handleWelcomeSubmit}
        okText="保存"
        width={400}
      >
        <Form form={welcomeForm} layout="vertical">
          <Form.Item name="welcome_enabled" label="启用欢迎语" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item
            name="welcome_message"
            label="欢迎语内容"
            extra="可用 {name} 代替入群用户名称"
          >
            <Input.TextArea rows={4} placeholder="欢迎 {name} 加入群聊！" />
          </Form.Item>
        </Form>
      </Drawer>

      <Drawer
        title="AI对话配置"
        open={isAIOpen}
        onClose={() => setIsAIOpen(false)}
        onOk={handleAISubmit}
        okText="保存"
        width={400}
      >
        <Form form={aiForm} layout="vertical">
          <Form.Item name="ai_enabled" label="启用AI对话" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="ai_sleep_start" label="休眠开始时间" extra="默认 23:00">
            <Input placeholder="23:00" />
          </Form.Item>
          <Form.Item name="ai_sleep_end" label="休眠结束时间" extra="默认 07:00">
            <Input placeholder="07:00" />
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  );
};

export default Groups;
