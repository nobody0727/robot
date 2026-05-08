import React, { useState } from 'react';
import { Table, Card, Input, Space, Tag, Select, DatePicker, Button } from 'antd';
import { SearchOutlined, FilterOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { messagesApi } from '../../api/messages';
import { groupsApi } from '../../api/groups';
import type { GroupMessage, BotGroup } from '../../types';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const Messages: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<GroupMessage[]>([]);
  const [groups, setGroups] = useState<BotGroup[]>([]);
  const [pagination, setPagination] = useState({ total: 0, page: 1, pageSize: 20 });
  const [filters, setFilters] = useState({
    keyword: '',
    group_id: undefined as number | undefined,
    msg_type: undefined as string | undefined,
    start_date: undefined as string | undefined,
    end_date: undefined as string | undefined,
  });

  useEffect(() => {
    fetchGroups();
  }, []);

  useEffect(() => {
    fetchData();
  }, [pagination.page, pagination.pageSize, filters]);

  const fetchGroups = async () => {
    try {
      const result = await groupsApi.getList({ page_size: 1000 });
      setGroups(result.items);
    } catch (error) {
      console.error('Failed to fetch groups:', error);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await messagesApi.getList({
        page: pagination.page,
        page_size: pagination.pageSize,
        ...filters,
      });
      setMessages(result.items);
      setPagination((prev) => ({ ...prev, total: result.total }));
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setFilters({ ...filters, keyword: value });
    setPagination({ ...pagination, page: 1 });
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters({ ...filters, [key]: value });
    setPagination({ ...pagination, page: 1 });
  };

  const handleDateChange = (dates: any) => {
    if (dates) {
      setFilters({
        ...filters,
        start_date: dates[0]?.toISOString(),
        end_date: dates[1]?.toISOString(),
      });
      setPagination({ ...pagination, page: 1 });
    }
  };

  const getMsgTypeTag = (type: string) => {
    const typeMap: Record<string, { color: string; label: string }> = {
      text: { color: 'default', label: '文本' },
      recall: { color: 'orange', label: '撤回' },
      join: { color: 'green', label: '入群' },
      leave: { color: 'red', label: '退群' },
      image: { color: 'purple', label: '图片' },
      video: { color: 'magenta', label: '视频' },
      voice: { color: 'cyan', label: '语音' },
    };
    const config = typeMap[type] || { color: 'default', label: type };
    return <Tag color={config.color}>{config.label}</Tag>;
  };

  const columns = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '群组',
      dataIndex: 'group_name',
      key: 'group_name',
      width: 120,
      render: (text: string, record: GroupMessage) =>
        text || record.group_id,
    },
    {
      title: '发送者',
      dataIndex: 'sender_name',
      key: 'sender_name',
      width: 120,
      render: (text: string, record: GroupMessage) => (
        <div>
          <div>{text || '未知用户'}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.sender_id}</div>
        </div>
      ),
    },
    {
      title: '类型',
      dataIndex: 'msg_type',
      key: 'msg_type',
      width: 80,
      render: getMsgTypeTag,
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      render: (text: string, record: GroupMessage) => (
        <div
          style={{
            maxWidth: 400,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            color: record.is_recalled ? '#999' : 'inherit',
            textDecoration: record.is_recalled ? 'line-through' : 'none',
          }}
        >
          {text}
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_recalled',
      key: 'is_recalled',
      width: 80,
      render: (isRecalled: boolean) =>
        isRecalled ? <Tag color="orange">已撤回</Tag> : '-',
    },
  ];

  return (
    <div className="fade-in">
      <h1 style={{ marginBottom: 16 }}>消息管理</h1>

      <div className="table-filters">
        <Input.Search
          placeholder="搜索消息内容"
          allowClear
          style={{ width: 250 }}
          prefix={<SearchOutlined />}
          onSearch={handleSearch}
        />
        <Select
          placeholder="选择群组"
          allowClear
          style={{ width: 150 }}
          onChange={(value) => handleFilterChange('group_id', value)}
          options={groups.map((g) => ({
            label: g.room_name || g.room_id,
            value: g.id,
          }))}
        />
        <Select
          placeholder="消息类型"
          allowClear
          style={{ width: 100 }}
          onChange={(value) => handleFilterChange('msg_type', value)}
          options={[
            { label: '文本', value: 'text' },
            { label: '入群', value: 'join' },
            { label: '退群', value: 'leave' },
          ]}
        />
        <RangePicker
          showTime
          onChange={handleDateChange}
          style={{ width: 350 }}
        />
      </div>

      <Table
        columns={columns}
        dataSource={messages}
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
    </div>
  );
};

export default Messages;
