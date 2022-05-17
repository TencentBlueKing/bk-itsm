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
  <div class="devops-preview" :class="{ 'full-screen': isFullScreen }">
    <header class="devops-header">
      <i v-if="!isFullScreen" class="bk-itsm-icon icon-order-open" @click.stop="openFullScreen()"></i>
      <span v-else class="exit-full-screen" @click.stop="onCloseFullScreen">
        <i class="bk-itsm-icon icon-order-close"></i>
        <span class="exit-text">{{$t(`m.common['退出全屏']`)}}</span>
      </span>
    </header>
    <section class="devops-preview-wrap">
      <div class="devops-preview-body">
        <div class="stage" v-for="(stage, sIndex) in stages" :key="stage.id">
          <span class="stage-connect-line"></span>
          <h4 class="stage-name">{{ stage.name }}</h4>
          <ul class="containers" v-for="(container, cIndex) in stage.containers" :key="container.id">
            <svg
              v-if="sIndex !== 0"
              xmlns="http://www.w3.org/2000/svg"
              xmlns:xlink="http://www.w3.org/1999/xlink"
              width="60"
              :style="getSvgStyle(stage, cIndex)"
              :height="cIndex === 0 ? 70 : (stage.containers[cIndex - 1].elements.length + 1) * 56"
              class="container-connect-line left">
              <path :d="getPath(stage, cIndex)"></path>
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg"
              xmlns:xlink="http://www.w3.org/1999/xlink"
              width="60"
              :style="getSvgStyle(stage, cIndex)"
              :height="cIndex === 0 ? 70 : (stage.containers[cIndex - 1].elements.length + 1) * 56"
              class="container-connect-line">
              <path :d="getPath(stage, cIndex)"></path>
            </svg>
            <li class="element container-title">
              {{ container.name }}
              <span v-if="sIndex !== 0" class="semicircle"></span>
              <span v-if="sIndex !== 0" class="triangle"></span>
            </li>
            <li v-for="element in container.elements"
              :key="element.id"
              :class="['element', { 'not-execute': !isElementCanExecute(element) }]">
              {{ element.name }}
            </li>
          </ul>
        </div>
      </div>
      <div v-if="loading" class="loading">
        <i class="bk-itsm-icon icon-icon-loading"></i>
        <span>{{ $t(`m.tickets['预览正在加载中']`) }}</span>
      </div>
    </section>
  </div>
</template>

<script>

  export default {
    name: 'DevopsPreview',
    components: {},
    props: {
      stages: {
        type: Array,
        default: () => ([]),
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        isFullScreen: false,
      };
    },
    methods: {
      // 当前操作节点打开全屏
      openFullScreen() {
        this.isFullScreen = true;
        this.$bkMessage({
          message: this.$t('m.common["按 ESC 键退出全屏"]'),
        });
        document.addEventListener('keydown', this.handlerKeyDown);
      },
      // 关闭全屏
      onCloseFullScreen() {
        this.isFullScreen = false;
      },
      // 关闭全屏 - esc
      handlerKeyDown(event) {
        if (event.keyCode === 27) {
          this.onCloseFullScreen();
          document.removeEventListener('keydown', this.handlerKeyDown);
        }
      },
      getPath(stage, index) {
        if (index === 0) {
          return 'M 60 2 L 55 2 Q 50 2 50 7 L 50 60 Q 50 62 45 62 L 0 62';
        }
        const height = (stage.containers[index - 1].elements.length + 1) * 56;
        return `M 50 2 L 50 ${height - 10} Q 50 ${height - 5} 45 ${height - 5} L 0 ${height - 5}`;
      },
      getSvgStyle(stage, index) {
        if (index === 0) {
          return '';
        }
        const height = (stage.containers[index - 1].elements.length + 1) * 56;
        const top = height - 27;
        return top ? `top: ${-top}px;` : '';
      },
      isElementCanExecute(element) {
        if (!element.additionalOptions || !element.additionalOptions.runCondition) {
          return true;
        }
        const { runCondition, customVariables, enable } = element.additionalOptions;
        if (!enable) {
          return false;
        }
        switch (runCondition) {
          case 'CUSTOM_VARIABLE_MATCH': {
            const allVarCheck = customVariables.every(varible => !!varible.value);
            return allVarCheck;
          }
          case 'CUSTOM_VARIABLE_MATCH_NOT_RUN': {
            const allVarCheck2 = customVariables.every(varible => !!varible.value);
            return !allVarCheck2;
          }
          default: {
            return true;
          }
        }
      },
    },
  };
</script>
<style lang='scss' scoped>
@import '../../scss/animation/rotation.scss';

.devops-preview {
    margin-top: 8px;
    width: 100%;
    height: 291px;
    background: #fafbfd;
    border: 1px solid #cacedb;
    &.full-screen {
        margin: 0;
        position: fixed;
        left: 0;
        top: 0;
        z-index: 999;
        width: 100%;
        height: 100%;
        overflow: auto;
        border: none;
        .devops-header {
            height: 52px;
            line-height: 52px;
            background: #313238;
            color: #fff;
        }
    }
    .devops-header {
        padding-right: 4px;
        height: 21px;
        line-height: 21px;
        color: #979ba5;
        background: #f0f1f5;
        font-size: 14px;
        text-align: right;
        > .bk-itsm-icon, > .exit-full-screen {
            cursor: pointer;
        }
        .exit-full-screen {
            display: inline-block;
            padding: 0 20px;
            &:hover {
                background: #000000;
            }
        }
    }
    .devops-preview-wrap {
        position: relative;
        height: calc(100% - 21px);
        overflow: auto;
        .devops-preview-body {
            white-space: nowrap;
            padding: 16px 43px;
            padding-bottom: 30px;
            font-size: 14px;
            width: fit-content;
            .stage {
                position: relative;
                display: inline-block;
                vertical-align: top;
                padding-bottom: 16px;
                width: 280px;
                background: #f0f1f5;
                border-radius: 2px;
                &::before {
                    position: absolute;
                    left: -6px;
                    top: 18px;
                    content: '';
                    width: 0px;
                    height: 0px;
                    border: 7px solid #c4c6cc;
                    z-index: 4;
                    border-color: transparent transparent transparent #c4c6cc;
                }
                &::after {
                    position: absolute;
                    right: -5px;
                    top: 20px;
                    content: '';
                    width: 6px;
                    height: 10px;
                    background: #c4c6cc;
                    z-index: 4;
                    border-radius: 0px 10px 10px 0px;
                }
                &:first-child::before {
                    display: none;
                }
                &:not(:first-child) {
                    margin-left: 80px;
                }
                .stage-connect-line {
                    position: absolute;
                    right: -75px;
                    top: 24px;
                    width: 70px;
                    height: 2px;
                    background: #c4c6cc;
                    z-index: 4;
                }
                .stage-name {
                    margin: 0;
                    height: 50px;
                    line-height: 50px;
                    text-align: center;
                    background: #f0f1f5;
                    border: 1px solid #c4c6cc;
                    border-radius: 2px;
                    color: #313238;
                    font-weight: normal;
                }
                .containers {
                    position: relative;
                    padding: 0 20px;
                    .element {
                        padding-left: 14px;
                        position: relative;
                        margin-top: 12px;
                        height: 42px;
                        line-height: 42px;
                        text-align: left;
                        color: #63656E;
                        background: #ffffff;
                        border: 1px solid #dcdee5;
                        &.not-execute {
                            color: #979BA5;
                            opacity: 0.5;
                            text-decoration: line-through;
                        }
                        &.container-title {
                            color: #ffffff;
                            font-weight: 700;
                            background: #64656e;
                            .semicircle {
                                position: absolute;
                                left: -7px;
                                top: 14px;
                                content: '';
                                width: 0px;
                                height: 0px;
                                border: 7px solid #c4c6cc;
                                z-index: 4;
                                border-color: transparent transparent transparent #c4c6cc;
                            }
                            .triangle {
                                position: absolute;
                                right: -6px;
                                top: 16px;
                                content: '';
                                width: 6px;
                                height: 10px;
                                background: #c4c6cc;
                                z-index: 4;
                                border-radius: 0px 10px 10px 0px;
                            }
                        }
                        &::before {
                            position: absolute;
                            content: '';
                            left: 20px;
                            bottom: -12px;
                            width: 2px;
                            height: 12px;
                            background: #c4c6cc;
                        }
                        &::after {
                            position: absolute;
                            content: '';
                            left: 16px;
                            bottom: -17px;
                            width: 6px;
                            height: 6px;
                            background: #ffffff;
                            border: 2px solid #c4c6cc;
                            border-radius: 50%;
                            z-index: 1;
                        }
                    }
                    &:last-child {
                        .element:last-child {
                            &::before, &::after {
                                display: none;
                            }
                        }
                    }
                }
            }
        }
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: #fafbfd;
            z-index: 99;
            color: #63656e;
            .bk-itsm-icon.icon-icon-loading {
                @include rotation;
                margin-right: 10px;
                font-size: 26px;
                color: #3A84FF;
            }
        }
    }
}

.container-connect-line {
    position: absolute;
    right: -40px;
    top: -39px;
    z-index: 0;
    fill: none;
    &.left {
        left: -40px;
        transform: rotateY(180deg);
    }
    path {
        stroke: #c4c6cc;
    }
}
</style>
