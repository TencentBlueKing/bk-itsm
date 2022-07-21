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
  <div class="bar-chart-wrap" ref="barChartWrap">
    <canvas class="bar-chart" :height="height"></canvas>
  </div>
</template>
<script>
  import Chart from '@blueking/bkcharts';

  export default {
    name: 'BarChart',
    props: {
      title: {
        type: String,
        default: '',
      },
      desc: {
        type: String,
        default: '',
      },
      xAxisName: {
        type: String,
        default: '',
      },
      yAxisName: {
        type: String,
        default: '',
      },
      height: {
        type: Number,
        default: 320,
      },
      chartData: {
        type: Object,
        default() {
          return {
            x: [],
            y: [],
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
        const ctx = this.$refs.barChartWrap.querySelector('.bar-chart').getContext('2d');
        const { x, y } = this.chartData;
        this.chartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: x,
            datasets: [{
              data: y,
              backgroundColor: '#4b78c1',
              maxBarThickness: 24,
            }],
          },
          options: {
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false,
              },
            },
            scales: {
              x: {
                gridLines: {
                  display: false,
                },
              },
              y: {
                gridLines: {
                  borderDash: [5, 3],
                },
              },
            },
            interaction: {
              mode: 'nearest',
            },
          },
        });
      },
      updateChart() {
        this.chartInstance.data.datasets[0].data = this.chartData.y;
        this.chartInstance.data.labels = this.chartData.x;
        this.chartInstance.update();
      },
    },
  };
</script>
<style lang="scss" scoped>

</style>
