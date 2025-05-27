// API基础URL，指向端口5000
const API_BASE_URL = 'http://localhost:5000';

// 当前页码和每页显示数量
let currentPage = 1;
let pageSize = 10;

// 初始化图表（新增 playcollectChart）
const playloadChart = echarts.init(document.getElementById('playload-chart'));
const playlikeChart = echarts.init(document.getElementById('playlike-chart'));
const playcollectChart = echarts.init(document.getElementById('playcollect-chart'));

// 获取播放互动数据（拆分后分别渲染两张图表）
function fetchPlaylikeData() {
    fetch(`${API_BASE_URL}/playLike`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            renderPlaylikeChart(data);    // 渲染播放量-点赞量图表
            renderPlaycollectChart(data); // 渲染播放量-收藏量图表
        })
        .catch(error => {
            console.error('获取播放互动数据失败:', error);
            alert('获取播放互动数据失败，请检查API连接');
        });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 获取并展示排行榜数据
    fetchRankList(currentPage, pageSize);

    // 获取并展示播放量与弹幕量关系图
    fetchPlayloadData();

    // 获取并展示播放量、点赞量与收藏量关系图
    fetchPlaylikeData();

    // 绑定分页按钮事件
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchRankList(currentPage, pageSize);
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        const totalPages = parseInt(document.getElementById('total-pages').textContent);
        if (currentPage < totalPages) {
            currentPage++;
            fetchRankList(currentPage, pageSize);
        }
    });

    // 绑定每页显示数量变更事件
    document.getElementById('page-size').addEventListener('change', (e) => {
        pageSize = parseInt(e.target.value);
        currentPage = 1; // 重置为第一页
        fetchRankList(currentPage, pageSize);
    });

    // 监听窗口大小变化，调整图表尺寸
    window.addEventListener('resize', () => {
        playloadChart.resize();
        playlikeChart.resize();
    });
});

// 获取排行榜数据
function fetchRankList(page, limit) {
    fetch(`${API_BASE_URL}/rankList?page=${page}&limit=${limit}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            renderRankList(data.data, page, data.pagination.total_pages, data.pagination.total_count);

            // 更新数据概览
            document.getElementById('total-videos').textContent = data.pagination.total_count.toLocaleString();

            // 计算平均播放量和点赞量
            if (data.data.length > 0) {
                const totalPlay = data.data.reduce((sum, video) => sum + parseInt(video.播放量)*10000, 0);
                const totalLike = data.data.reduce((sum, video) => sum + parseInt(video.点赞量)*10000, 0);

                document.getElementById('avg-play').textContent = Math.round(totalPlay / data.data.length).toLocaleString();
                document.getElementById('avg-like').textContent = Math.round(totalLike / data.data.length).toLocaleString();
            }
        })
        .catch(error => {
            console.error('获取排行榜数据失败:', error);
            alert('获取排行榜数据失败，请检查API连接');
        });
}

// 渲染排行榜列表
function renderRankList(data, page, totalPages, totalCount) {
    const tableBody = document.getElementById('rank-table-body');
    tableBody.innerHTML = '';

    // 计算排名起始值
    const startRank = (page - 1) * pageSize + 1;

    data.forEach((video, index) => {
        const rank = startRank + index;
        const row = document.createElement('tr');
        row.className = rank % 2 === 0 ? 'bg-gray-50' : 'bg-white';
        row.innerHTML = `
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <span class="font-semibold ${rank <= 3 ? 'text-primary' : ''}">${rank}</span>
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <a href="${video.视频链接}" target="_blank" class="text-secondary hover:underline">${video.视频名称}</a>
                </div>
            </td>
            <td class="px-6 py-4">${video.UP主}</td>
            <td class="px-6 py-4">${video.发布时间}</td>
            <td class="px-6 py-4">${parseInt(video.播放量).toLocaleString()+'w'}</td>
            <td class="px-6 py-4">${parseInt(video.点赞量).toLocaleString()+'w'}</td>
        `;
        tableBody.appendChild(row);
    });

    // 更新分页信息
    document.getElementById('current-page').textContent = page;
    document.getElementById('total-pages').textContent = totalPages;

    // 禁用/启用分页按钮
    document.getElementById('prev-page').disabled = page === 1;
    document.getElementById('next-page').disabled = page === totalPages;
}

// 获取播放量与弹幕量关系数据
function fetchPlayloadData() {
    fetch(`${API_BASE_URL}/playLoad`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            renderPlayloadChart(data);
        })
        .catch(error => {
            console.error('获取播放弹幕数据失败:', error);
            alert('获取播放弹幕数据失败，请检查API连接');
        });
}

// 渲染播放量与弹幕量关系图
function renderPlayloadChart(data) {
    // 处理数据
    const chartData = data.data.map(item => {
        return [
            parseInt(item.播放量),
            parseInt(item.弹幕量),
            item.视频名称
        ];
    });

    // 配置图表选项
    const option = {
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `
                    <div class="font-bold">${params.data[2]}</div>
                    <div>播放量: ${parseInt(params.data[0]).toLocaleString() + 'w'}</div>
                    <div>弹幕量: ${parseInt(params.data[1]).toLocaleString()}</div>
                `;
            }
        },
        xAxis: {
            name: '播放量',
            type: 'value',
            scale: true,
            nameLocation: 'middle',
            nameGap: 25,
            axisLabel: {
                formatter: function(value) {
                    return (value).toFixed(1) + '万';
                }
            }
        },
        yAxis: {
            name: '弹幕量',
            type: 'value',
            scale: true,
            nameLocation: 'middle',
            nameGap: 30,
            axisLabel: {
                formatter: function(value) {
                    if (value >= 10000) {
                        return (value / 10000).toFixed(1) + '万';
                    }
                    return value;
                }
            }
        },
        series: [{
            name: '视频',
            type: 'scatter',
            data: chartData,
            symbolSize: 10,
            itemStyle: {
                color: '#FB7299',
                opacity: 0.7
            },
            emphasis: {
                itemStyle: {
                    opacity: 1
                }
            }
        }]
    };

    // 设置图表选项
    playloadChart.setOption(option);
}

// 渲染播放量与点赞量关系图
function renderPlaylikeChart(data) {
    const chartData = data.data.map(item => {
        return [
            parseInt(item.播放量),
            parseInt(item.点赞量),
            item.视频名称
        ];
    });

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `
                    <div class="font-bold">${params.data[2]}</div>
                    <div>播放量: ${parseInt(params.data[0]).toLocaleString() + 'w'}</div>
                    <div>点赞量: ${parseInt(params.data[1]).toLocaleString()}</div>
                `;
            }
        },
        xAxis: {
            name: '播放量',
            type: 'value',
            scale: true,
            nameLocation: 'middle',
            nameGap: 25,
            axisLabel: { formatter: val => (val).toFixed(1) + '万' }
        },
        yAxis: {
            name: '点赞量',
            type: 'value',
            scale: true,
            nameLocation: 'middle',
            nameGap: 30,
            axisLabel: {
                formatter: val => (val >= 10000 ? (val / 10000).toFixed(1) + '万' : val)
            }
        },
        series: [{
            name: '视频',
            type: 'scatter',
            data: chartData,
            symbolSize: data => Math.max(5, data[1] / 10000), // 点赞量越大点越大
            itemStyle: { color: '#FB7299', opacity: 0.7 },
            emphasis: { itemStyle: { opacity: 1 } }
        }]
    };
    playlikeChart.setOption(option);
}

// 渲染播放量与收藏量关系图
function renderPlaycollectChart(data) {
    const chartData = data.data.map(item => {
        return [
            parseInt(item.播放量),
            parseInt(item.收藏量),
            item.视频名称
        ];
    });

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `
                    <div class="font-bold">${params.data[2]}</div>
                    <div>播放量: ${parseInt(params.data[0]).toLocaleString() + 'w'}</div>
                    <div>收藏量: ${parseInt(params.data[1]).toLocaleString()}</div>
                `;
            }
        },
        xAxis: {
            name: '播放量',
            type: 'value',
            scale: true,
            nameLocation: 'middle',
            nameGap: 25,
            axisLabel: { formatter: val => (val).toFixed(1) + '万' }
        },
        yAxis: {
            name: '收藏量',
            type: 'value',
            scale: true,
            nameLocation: 'middle',
            nameGap: 30,
            axisLabel: {
                formatter: val => (val >= 10000 ? (val / 10000).toFixed(1) + '万' : val)
            }
        },
        series: [{
            name: '视频',
            type: 'scatter',
            data: chartData,
            symbolSize: data => Math.max(5, data[1] / 10000), // 收藏量越大点越大
            itemStyle: { color: '#23ADE5', opacity: 0.7 },
            emphasis: { itemStyle: { opacity: 1 } }
        }]
    };
    playcollectChart.setOption(option);
}