import React, { useState } from 'react';
import { Card, Statistic, Row, Col, Spin } from 'antd';
import {
  TeamOutlined,
  MessageOutlined,
  UserOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { useEffect } from 'react';
import { dashboardApi } from '../../api/dashboard';
import type { DashboardOverview } from '../../types';
import { Bar, Pie } from '@ant-design/charts';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardOverview | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await dashboardApi.getOverview();
      setData(result);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  const trendData = data.message_trend.map((item) => ({
    date: item.date,
    count: item.count,
  }));

  const trendConfig = {
    data: trendData,
    xField: 'date',
    yField: 'count',
    label: {
      position: 'middle' as const,
      style: { fill: '#FFFFFF', opacity: 0.6 },
    },
    meta: {
      date: { alias: '日期' },
      count: { alias: '消息数' },
    },
  };

  const topGroupData = data.top_groups.map((item) => ({
    name: item.name,
    value: item.message_count,
  }));

  const pieConfig = {
    data: topGroupData,
    angleField: 'value',
    colorField: 'name',
    radius: 0.8,
    label: {
      type: 'inner' as const,
      offset: '-30%',
      content: '{percentage}',
      style: {
        textAlign: 'center' as const,
        fontSize: 14,
      },
    },
    legend: {
      position: 'right' as const,
    },
  };

  return (
    <div className="fade-in">
      <h1 style={{ marginBottom: 24 }}>仪表盘概览</h1>
      
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="活跃群组数"
              value={data.total_groups}
              prefix={<TeamOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="7天消息数"
              value={data.total_messages_7d}
              prefix={<MessageOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="白名单用户"
              value={data.total_whitelist_users}
              prefix={<UserOutlined style={{ color: '#722ed1' }} />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="7天活跃用户"
              value={data.active_users_7d}
              prefix={<RiseOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="消息趋势 (7天)">
            <Bar {...trendConfig} height={300} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="热门群组">
            {topGroupData.length > 0 ? (
              <Pie {...pieConfig} height={300} />
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                暂无数据
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
