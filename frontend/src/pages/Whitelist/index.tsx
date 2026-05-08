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
  Select,
  DatePicker,
  Upload,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  DeleteOutlined,
  DownloadOutlined,
  UploadOutlined,
  EditOutlined,
} from '@ant-design/icons';
import { useEffect } from 'react';
import { whitelistApi } from '../../api/whitelist';
import type { WhitelistUser, WhitelistStats } from '../../types';
import dayjs from 'dayjs';
import { useAuthStore } from '../../stores/authStore';

const Whitelist: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<WhitelistUser[]>([]);
  const [stats, setStats] = useState<WhitelistStats | null>(null);
  const [pagination, setPagination] = useState({ total: 0, page: 1, pageSize: 20 });
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<WhitelistUser | null>(null);
  const [form] = Form.useForm();
  const { user } = useAuthStore();

  useEffect(() => {
    fetchData();
    fetchStats();
  }, [pagination.page, pagination.pageSize, searchKeyword]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await whitelistApi.getList({
        page: pagination.page,
        page_size: pagination.pageSize,
        keyword: searchKeyword || undefined,
      });
      setUsers(result.items);
      setPagination((prev) => ({ ...prev, total: result.total }));
    } catch (error) {
      message.error('获取白名单失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const result = await whitelistApi.getStats();
      setStats(result);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleAdd = () => {
    setEditingUser(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (record: WhitelistUser) => {
    setEditingUser(record);
    form.setFieldsValue({
      user_id: record.user_id,
      user_name: record.user_name,
      remark: record.remark,
      expire_at: record.expire_at ? dayjs(record.expire_at) : null,
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await whitelistApi.delete(id);
      message.success('删除成功');
      fetchData();
      fetchStats();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const data = {
        user_id: values.user_id,
        user_name: values.user_name,
        remark: values.remark,
        expire_at: values.expire_at?.toISOString(),
      };

      if (editingUser) {
        await whitelistApi.update(editingUser.id, data);
        message.success('更新成功');
      } else {
        await whitelistApi.create(data);
        message.success('添加成功');
      }

      setIsModalOpen(false);
      fetchData();
      fetchStats();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleExport = async () => {
    try {
      const result = await whitelistApi.export();
      const csvContent = [
        ['user_id', 'user_name', 'added_at', 'expire_at', 'remark', 'is_active'],
        ...result.items.map((item) => [
          item.user_id,
          item.user_name || '',
          item.added_at,
          item.expire_at || '',
          item.remark || '',
          item.is_active ? '是' : '否',
        ]),
      ]
        .map((row) => row.join(','))
        .join('\n');

      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `whitelist_${dayjs().format('YYYYMMDD')}.csv`;
      link.click();
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const columns = [
    {
      title: '用户ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 180,
    },
    {
      title: '昵称',
      dataIndex: 'user_name',
      key: 'user_name',
      width: 120,
    },
    {
      title: '添加人',
      dataIndex: 'added_by_name',
      key: 'added_by_name',
      width: 100,
    },
    {
      title: '添加时间',
      dataIndex: 'added_at',
      key: 'added_at',
      width: 170,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '过期时间',
      dataIndex: 'expire_at',
      key: 'expire_at',
      width: 170,
      render: (text: string) =>
        text ? dayjs(text).format('YYYY-MM-DD HH:mm') : '-',
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
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: WhitelistUser) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除?"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>白名单管理</h1>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加白名单
          </Button>
        </Space>
      </div>

      {stats && (
        <Card size="small" style={{ marginBottom: 16 }}>
          <Space size="large">
            <span>总数: <strong>{stats.total}</strong></span>
            <span>启用: <strong>{stats.active}</strong></span>
            <span>今日新增: <strong>{stats.added_today}</strong></span>
            <span>即将过期: <strong>{stats.expire_soon}</strong></span>
          </Space>
        </Card>
      )}

      <div className="table-filters">
        <Input.Search
          placeholder="搜索用户ID或昵称"
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
        dataSource={users}
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
        title={editingUser ? '编辑白名单用户' : '添加白名单用户'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => setIsModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="user_id"
            label="用户ID (微信号)"
            rules={[{ required: true, message: '请输入用户ID' }]}
          >
            <Input placeholder="请输入微信ID" disabled={!!editingUser} />
          </Form.Item>
          <Form.Item name="user_name" label="昵称">
            <Input placeholder="请输入昵称（可选）" />
          </Form.Item>
          <Form.Item name="expire_at" label="过期时间">
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea rows={3} placeholder="请输入备注（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Whitelist;
