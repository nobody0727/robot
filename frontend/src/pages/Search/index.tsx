import React, { useState } from 'react';
import { Card, Input, Button, Select, Space, List, Tag, Spin, Empty } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { searchApi } from '../../api/search';
import { groupsApi } from '../../api/groups';
import type { SearchResult, BotGroup, SemanticSearchResponse } from '../../types';
import dayjs from 'dayjs';
import Highlight from 'react-highlight-words';

const Search: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [searchType, setSearchType] = useState<'semantic' | 'keyword'>('semantic');
  const [selectedGroup, setSelectedGroup] = useState<number | undefined>();
  const [groups, setGroups] = useState<BotGroup[]>([]);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searchInfo, setSearchInfo] = useState<SemanticSearchResponse | null>(null);

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const result = await groupsApi.getList({ page_size: 1000 });
      setGroups(result.items);
    } catch (error) {
      console.error('Failed to fetch groups:', error);
    }
  };

  const handleSearch = async () => {
    if (!keyword.trim()) return;

    try {
      setLoading(true);
      setResults([]);
      setSearchInfo(null);

      if (searchType === 'semantic') {
        const response = await searchApi.semantic({
          query: keyword,
          group_id: selectedGroup,
          top_k: 10,
        });
        setResults(response.results);
        setSearchInfo(response);
      } else {
        const response = await searchApi.keyword({
          keyword,
          group_id: selectedGroup,
        });
        setResults(response.results);
        setSearchInfo({
          query: keyword,
          expanded_keywords: [keyword],
          synonyms: [],
          results: response.results,
          total: response.total,
          search_time_ms: 0,
        });
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <h1 style={{ marginBottom: 24 }}>智能搜索</h1>

      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Space wrap>
            <Select
              value={searchType}
              onChange={setSearchType}
              style={{ width: 120 }}
              options={[
                { label: '语义搜索', value: 'semantic' },
                { label: '关键词搜索', value: 'keyword' },
              ]}
            />
            <Select
              placeholder="选择群组（可选）"
              allowClear
              style={{ width: 200 }}
              value={selectedGroup}
              onChange={setSelectedGroup}
              options={groups.map((g) => ({
                label: g.room_name || g.room_id,
                value: g.id,
              }))}
            />
          </Space>
          <Space.Compact style={{ width: '100%' }}>
            <Input
              placeholder={
                searchType === 'semantic'
                  ? '输入自然语言查询，如：查找关于项目进度的讨论'
                  : '输入关键词搜索'
              }
              size="large"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onPressEnter={handleSearch}
              prefix={<SearchOutlined />}
            />
            <Button type="primary" size="large" onClick={handleSearch} loading={loading}>
              搜索
            </Button>
          </Space.Compact>

          {searchType === 'semantic' && (
            <div style={{ color: '#666', fontSize: 13 }}>
              💡 语义搜索会使用AI扩展查询关键词，结合向量相似度和文本匹配进行混合检索
            </div>
          )}
        </Space>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>搜索中...</div>
        </div>
      )}

      {searchInfo && !loading && (
        <Card style={{ marginBottom: 24 }}>
          <div style={{ marginBottom: 16 }}>
            <strong>搜索词：</strong>{searchInfo.query}
          </div>
          {searchInfo.expanded_keywords.length > 0 && (
            <div style={{ marginBottom: 8 }}>
              <strong>扩展关键词：</strong>
              {searchInfo.expanded_keywords.map((kw) => (
                <Tag color="blue" key={kw} style={{ marginRight: 4 }}>
                  {kw}
                </Tag>
              ))}
            </div>
          )}
          <div>
            <span>找到 {searchInfo.total} 条相关结果</span>
            <span style={{ marginLeft: 16, color: '#999' }}>
              搜索耗时 {searchInfo.search_time_ms}ms
            </span>
          </div>
        </Card>
      )}

      {!loading && results.length === 0 && searchInfo && (
        <Empty description="未找到相关消息" />
      )}

      {!loading && results.length > 0 && (
        <List
          itemLayout="vertical"
          dataSource={results}
          renderItem={(item) => (
            <List.Item>
              <div className="search-result">
                <div className="search-result-header">
                  <Space>
                    <Tag color="blue">{item.group_name || `群组${item.group_id}`}</Tag>
                    <span>👤 {item.sender_name || item.sender_id}</span>
                    <span style={{ color: '#999' }}>
                      {item.created_at ? dayjs(item.created_at).format('YYYY-MM-DD HH:mm') : ''}
                    </span>
                  </Space>
                  <span className="similarity-badge">
                    相关度 {Math.round((item.similarity || 0) * 100)}%
                  </span>
                </div>
                <div className="search-result-content">
                  <Highlight
                    searchWords={searchInfo?.expanded_keywords || []}
                    textToHighlight={item.content}
                    highlightStyle={{ backgroundColor: '#ffe58f', padding: '0 2px' }}
                  />
                </div>
              </div>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default Search;
