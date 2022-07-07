<!--
  - Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
  -
  - License for BK-ITSM 蓝鲸流程服务:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <div class="pie-chart-wrap" ref="pieChartWrap">
    <canvas class="pie-chart" style="width: 100%;" :height="height"></canvas>
  </div>
</template>
<script>
  import Chart from '@blueking/bkcharts';

  export default {
    name: 'PieChart',
    props: {
      height: {
        type: Number,
        default: 320,
      },
      chartData: {
        type: Object,
        default() {
          return {
            labels: [],
            value: [],
          };
        },
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        chartInstance: null,
      };
    },
    watch: {
      loading(val) {
        if (!val) {
          this.updateChart();
        }
      },
    },
    mounted() {
      this.init();
    },
    methods: {
      init() {
        const ctx = this.$refs.pieChartWrap.querySelector('.pie-chart').getContext('2d');
        const { labels, value } = this.chartData;
        this.chartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels,
            datasets: [{
              borderAlign: 'center',
              backgroundColor: [
                '#4b78c1',
                '#6ca0e4',
                '#a0b7da',
                '#6bc265',
                '#43bdb1',
                '#f29292',
                '#43bdb1',
                '#edb073',
                '#d8a6ef',
                '#f0a9a9',
              ],
              data: value,
            }],
          },
          options: {
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
              },
              tooltip: {
                callbacks: {
                  label(context) {
                    const total = context.dataset.data.reduce((a, c) => a + c);
                    const percent = (context.dataPoint / total * 100).toFixed(2);
                    return `${context.label}: ${percent}%`;
                  },
                },
              },
            },
          },
        });
      },
      updateChart() {
        this.chartInstance.data.datasets[0].data = this.chartData.value;
        this.chartInstance.data.labels = this.chartData.labels;
        this.chartInstance.update();
      },
    },
  };
</script>
<style lang="scss" scoped>

</style>
