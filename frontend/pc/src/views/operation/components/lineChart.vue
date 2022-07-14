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
  <div class="line-chart" ref="lineChartWrap">
    <div v-if="showTimeDimension" class="time-dimension-selector">
      <bk-select
        :clearable="false"
        :value="dimension"
        @selected="onSelectDimension">
        <bk-option
          v-for="item in timeDimensions"
          :key="item.key"
          :id="item.key"
          :name="item.name">
        </bk-option>
      </bk-select>
    </div>
    <canvas class="line-chart" :height="height"></canvas>
  </div>
</template>
<script>
  import Chart from '@blueking/bkcharts';
  import i18n from '@/i18n/index.js';

  export default {
    name: 'LineChart',
    props: {
      title: {
        type: String,
        default: '',
      },
      desc: {
        type: String,
        default: '',
      },
      showTimeDimension: {
        type: Boolean,
        default: true,
      },
      timeDimensions: {
        type: Array,
        default() {
          return [
            {
              key: 'days',
              name: i18n.t('m[\'天\']'),
            },
            {
              key: 'weeks',
              name: i18n.t('m[\'周\']'),
            },
            {
              key: 'months',
              name: i18n.t('m[\'月\']'),
            },
            {
              key: 'years',
              name: i18n.t('m[\'年\']'),
            },
          ];
        },
      },
      dimension: {
        type: String,
        default: '',
      },
      min: {
        type: Number,
        default: 0,
      },
      bgColor: {
        type: String,
        default: 'rgba(37,91,175,0.3)',
      },
      gradientColor: {
        type: Array,
        default: () => ([]),
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
        const ctx = this.$refs.lineChartWrap.querySelector('.line-chart').getContext('2d');
        const { x, y } = this.chartData;
        let bgColor;
        if (this.gradientColor.length === 2) {
          const gradient = ctx.createLinearGradient(0, 320, 0, 0);
          gradient.addColorStop(0, this.gradientColor[0]);
          gradient.addColorStop(1, this.gradientColor[1]);
          bgColor = gradient;
        } else {
          bgColor = this.bgColor;
        }

        this.chartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: x,
            datasets: [{
              data: y,
              fill: 'start',
              backgroundColor: bgColor,
              borderWidth: 0,
            }],
          },
          options: {
            maintainAspectRatio: false,
            // bezierCurve: false,
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
                ticks: {
                  precision: 0,
                },
                min: this.min,
              },
            },
            crosshair: {
              enabled: true,
            },
          },
        });
      },
      updateChart() {
        this.chartInstance.data.datasets[0].data = this.chartData.y;
        this.chartInstance.data.labels = this.chartData.x;
        this.chartInstance.update();
      },
      onSelectDimension(val) {
        this.$emit('onDimensionChange', val);
      },
    },
  };
</script>
<style lang="scss" scoped>
    .line-chart {
        position: relative;
        .time-dimension-selector {
            position: absolute;
            top: -38px;
            right: 0;
            width: 80px;
        }
    }
</style>
