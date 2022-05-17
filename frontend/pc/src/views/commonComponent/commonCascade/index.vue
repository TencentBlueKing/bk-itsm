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
  <div ref="cascader"
    class="bk-itsm-cascader"
    :class="{ visible: selector['open'] }"
    v-bk-clickoutside="closeHidden">
    <div @click="showcascader"
      class="bk-cascader bk-cascader-input bk-selector"
      :class="{ open: selector['open'] }">
      <input class="placeholder disabled"
        :class="{ fill: textinfo,focus: selector['open'] }"
        type="text"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        v-model="textinfo">
      <i class="bk-icon icon-angle-down bk-selector-icon" v-if="isactive"></i>
      <i class="bk-icon icon-circle-2-1 bk-selector-icon" v-else
        style="animation: bk-icon-button-loading 0.8s infinite linear;"></i>
    </div>
    <!-- 基础步骤 -->
    <div class="bk-search-input"
      :class="{
        'bk-search-input-one': (searchContent === ''),
        'bk-search-input-two': (searchContent === '' && options2.length),
        'bk-search-input-three': (searchContent === '' && options3.length)
      }">
      <input
        class="bk-cascade-search-input"
        ref="searchInput"
        type="text"
        placeholder="请搜索"
        v-model="searchContent">
    </div>
    <div class="bk-cascader bk-cascader-select" :style="styleObject" v-if="searchContent === ''">
      <ul class="bk-select bk-select-one" @scroll="scrollEvent">
        <li v-for="(item, index) in options1" :key="index" @scroll="scrollEvent">
          <!-- eslint-disable vue/camelcase -->
          <span @click="selectLevel(1,index,item)" class="bk-info-left"
            :class="{ signcolor: item['isselect'],bkCollect: index === 0 && iscollectTwo && isshowNumber }">
            <span>{{item.name}}</span>
            <span v-if="index === 0 && iscollectTwo && isshowNumber"
              style="margin-left: -8px;">
              {{'（' + (item.children && item.children.length ? item.children.length : 0) + '）'}}
            </span>
          </span>
          <!-- eslint-enable -->
          <span @click="selectLevel(1,index,item)" class="bk-info-right iconinfo"
            v-if="item.children && item.children.length">
            <i class="bk-icon icon-angle-right"></i>
          </span>
          <span class="bk-text-danger bk-info-right collect"
            :class="{ signcolor: options_favorites_sign.indexOf(item.key) !== -1 }"
            v-else-if="iscollectTwo && item.key !== 'favorites'">
            <i @click.stop.prevent="collect_s(item)"
              v-if="options_favorites_sign.indexOf(item.key) === -1"
              class="bk-icon icon-star"
              :title="$t(`m.common['添加收藏']`)">
            </i>
            <img @click.stop.prevent="collect_s(item)"
              v-else
              src="@/images/evaluate/starfill.svg"
              alt="starblank"
              :title="$t(`m.common['取消收藏']`)" />
            <!-- <span class="bk-tip-info bk-change" :style="styletranslateY">
                            <span class="bk-tooltips-arrows"></span>
                            <span v-if="options_favorites_sign.indexOf(item.key) === -1">
                                {{ $t('m.common["添加收藏"]') }}
                            </span>
                            <span v-else>{{ $t('m.common["取消收藏"]') }}</span>
                        </span> -->
          </span>
          <span class="bk-text-danger bk-info-right collect" v-else>
            <span class="bk-tip-info bk-change" :style="styletranslateY">
            </span>
          </span>
        </li>
        <div v-if="!options1 || !options1.length" style="height: 100%;text-align: center;padding-top:20px;">
          {{ $t('m.common["无数据"]') }}
        </div>
      </ul>
      <ul class="bk-select bk-select-two" v-if="options2 && options2.length">
        <li v-for="(item, index) in options2" :key="index">
          <span @click="selectLevel(2,index,item)" class="bk-info-left" :class="{ signcolor: item['isselect'] }">{{item.name}}</span>
          <span @click="selectLevel(2,index,item)" class="bk-info-right iconinfo"
            v-if="item.children && item.children.length">
            <i class="bk-icon icon-angle-right"></i>
          </span>
          <span class="bk-text-danger bk-info-right collect"
            :class="{ signcolor: options_favorites_sign.indexOf(item.key) !== -1 }"
            v-else-if="iscollectTwo && !item.favorites">
            <i @click.stop.prevent="collect_s(item)"
              v-if="options_favorites_sign.indexOf(item.key) === -1"
              class="bk-icon icon-star"
              :title="$t(`m.common['添加收藏']`)">
            </i>
            <img @click.stop.prevent="cancelcollect_s(item)"
              v-else
              src="@/images/evaluate/starfill.svg"
              alt="starblank"
              :title="$t(`m.common['取消收藏']`)" />
            <!-- <span class="bk-tip-info bk-change" :style="styletranslateY">
                            <span class="bk-tooltips-arrows"></span>
                            <span v-if="options_favorites_sign.indexOf(item.key) === -1">
                                {{ $t('m.common["添加收藏"]') }}
                            </span>
                            <span v-else>{{ $t('m.common["取消收藏"]') }}</span>
                        </span> -->
          </span>
          <span @click="cancelcollect_s(item, index)" class="bk-text-danger bk-info-right collect"
            v-else-if="item.favorites">
            <i class="bk-icon icon-close" v-if="true" style="font-size: 14px;"></i>
            <span class="bk-tip-info bk-change" :style="styletranslateY">
              <span class="bk-tooltips-arrows"></span>
              <span>{{ $t('m.common["取消收藏"]') }}</span>
            </span>
          </span>
          <span class="bk-text-danger bk-info-right collect" v-else>
            <span class="bk-tip-info bk-change" :style="styletranslateY">
            </span>
          </span>
        </li>
      </ul>
      <ul class="bk-select bk-select-three" v-if="options3 && options3.length">
        <li v-for="(item, index) in options3" :key="index">
          <span @click="selectLevel(3,index,item)" class="bk-info-left" :class="{ signcolor: item['isselect'] }">{{item.name}}</span>
          <span @click="selectLevel(3,index,item)" class="bk-info-right iconinfo"
            v-if="item.children && item.children.length">
            <i class="bk-icon icon-angle-right"></i>
          </span>
          <span class="bk-text-danger bk-info-right collect"
            :class="{ signcolor: options_favorites_sign.indexOf(item.key) !== -1 }"
            v-else-if="iscollectTwo">
            <i @click.stop.prevent="collect_s(item)"
              v-if="options_favorites_sign.indexOf(item.key) === -1"
              class="bk-icon icon-star"
              :title="$t(`m.common['添加收藏']`)">
            </i>
            <img @click.stop.prevent="collect_s(item)"
              v-else
              src="@/images/evaluate/starfill.svg"
              alt="starblank"
              :title="$t(`m.common['取消收藏']`)" />
            <!-- <span class="bk-tip-info bk-change" :style="styletranslateY">
                            <span class="bk-tooltips-arrows"></span>
                            <span v-if="options_favorites_sign.indexOf(item.key) === -1">
                                {{ $t('m.common["添加收藏"]') }}
                            </span>
                            <span v-else>{{ $t('m.common["取消收藏"]') }}</span>
                        </span> -->
          </span>
          <span class="bk-text-danger bk-info-right collect" v-else>
            <span class="bk-tip-info bk-change" :style="styletranslateY">
            </span>
          </span>
        </li>
      </ul>
    </div>
    <!-- 查询 -->
    <div class="bk-cascade-panel" v-if="searchContent !== ''">
      <ul class="bk-cascade-panel-ul" style="width: 100%">
        <li class="bk-option"
          v-for="(item, index) in searchList"
          :key="index"
          @click.prevent.stop="handleSelectItem(item, index)"
          :class="{
            'is-selected': item.isSelected,
            'is-disabled': item.disabled
          }">
          <div class="bk-option-content">
            <slot>
              <div class="bk-option-content-default" :title="item.name">
                <span class="bk-option-name">{{ item.name }}</span>
              </div>
            </slot>
          </div>
        </li>
        <li class="bk-option-none" v-if="!searchList.length">
          <span>暂无数据</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'commonCascader',
    model: {
      // 使用model， 这儿2个属性，prop属性说，我要将msg作为该组件被使用时（此处为aa组件被父组件调用）v-model能取到的值，event说，我emit ‘cc’ 的时候，参数的值就是父组件v-model收到的值。
      prop: 'textinfoOri',
      event: 'change',
    },
    props: {
      // model值
      textinfoOri: Array,
      // textinfoOri: {
      //     type: Array,
      //     default () {
      //         return []
      //     }
      // },
      positions: {
        type: Object,
        default() {
          return {
            top: '',
            left: '',
            bottom: '',
            right: '',
          };
        },
      },
      disabled: {
        type: Boolean,
        default() {
          return false;
        },
      },
      // 每级目录
      options: {
        type: Array,
        default() {
          return [];
        },
      },
      // 收藏样式二
      iscollectTwo: {
        type: Boolean,
        default() {
          return false;
        },
      },
      // 收藏项
      optionsFavorites: {
        type: Array,
        default() {
          return [];
        },
      },
      isshowNumber: {
        type: Boolean,
        default() {
          return false;
        },
      },
      isactive: {
        type: Boolean,
        default() {
          return false;
        },
      },
    },
    data() {
      return {
        // 数据结构实例
        options_eg: [{
          key: 'zhinan',
          name: this.$t('m.common["指南"]'),
          children: [{
            key: 'zujian',
            name: this.$t('m.common["组件"]'),
            children: [
              {
                key: 'basic',
                name: 'Basic',
              }, {
                key: 'form',
                name: 'Form',
                children: [{
                  key: 'radio',
                  name: this.$t('m.common["Radio 单选框"]'),
                }],
              },
            ],
          },
          ],
        }],
        isCollectOpen: true,
        // input框显示内容
        textinfo: '',
        placeholder: this.$t('m.common["请选择服务目录"]'),
        readonly: 'readonly',
        selector: {
          open: false,
        },
        selectedOptionsvalue: [],
        selectedOptions: [],
        styleObject: {
          // color: 'red',
          // fontSize: '13px'
          top: this.positions.top ? `${this.top}px` : null,
          left: this.positions.left ? `${this.left}px` : null,
          bottom: this.positions.bottom ? `${this.bottom}px` : null,
          right: this.positions.right ? `${this.right}px` : null,
        },
        options2: [],
        options3: [],
        level1: null,
        level2: null,
        level3: null,
        styletranslateY: {
          // visibility: 'hidden',
          // position: 'fixed',
          // color: 'red',
          // fontSize: '13px',
          transform: 'translate(-26px,-38px)',
        },
        // 搜索
        searchList: [],
        searchContent: '',
        searchItem: {},
      };
    },
    computed: {
      currentTextinfo() {
        return this.textinfoOri;
      },
      // 初始化 每级目录
      options1() {
        const options = (this.iscollectTwo && !this.iscollect_first) ? [this.favoritesItem, ...this.options] : [...this.options];
        if (options) {
          options.forEach((item) => {
            item.isselect = false;
          });
        }
        if (this.level1 !== null) {
          if (this.level1 === 0) {
            this.options2 = options[this.level1].children;
          }
          if (options[this.level1]) {
            options[this.level1].isselect = true;
          }
        }
        return options;
      },
      // 初始化 收藏项
      options_favorites_sign() {
        return this.optionsFavorites.map(item => item.key);
      },
      favoritesItem() {
        const favoritesItem = {
          key: 'favorites',
          name: this.$t('m.common["我的收藏"]'),
          children: [...this.optionsFavorites].map((item) => {
            item.favorites = true;
            return item;
          }),
        };
        return favoritesItem;
      },
      /* eslint-disable vue/no-async-in-computed-properties */
      async isTextinfoChange() {
        if (!this.textinfoOri || !this.textinfoOri.length) {
          // 清空
          if (this.selectedOptionsvalue && this.selectedOptionsvalue.length) {
            await this.reduction();
            return this.$t('m.common["清空"]');
          }
          return '==1';
        } if (this.textinfoOri.length !== this.selectedOptionsvalue.length) {
          // 赋值
          await this.assignment(this.textinfoOri);
          return this.$t('m.common["赋值1"]');
        } if (this.textinfoOri.length === this.selectedOptionsvalue.length) {
          let isChange = false;
          for (let i = 0; i < this.textinfoOri.length; i++) {
            if (this.selectedOptionsvalue[i].id !== this.textinfoOri[i].id) {
              isChange = true;
            }
          }
          if (isChange) {
            await this.assignment(this.textinfoOri);
            return this.$t('m.common["赋值2"]');
          }
          return '==2';
        }
        return '==3';
      },
      /* eslint-enable */
    },
    watch: {
      searchContent(val) {
        if (val) {
          this.getSearchList();
        }
      },
      'selector.open'(val) {
        if (val) {
          // 当弹开下拉框时，清空搜索数据
          this.searchContent = '';
        }
      },
      // 后期赋值响应
      async options1() {
        if (this.currentTextinfo && this.currentTextinfo.length && (this.textinfo !== await this.currentTextinfo.map(item => item.name).join('/'))) {
          this.assignment(this.currentTextinfo);
        }
      },
      async currentTextinfo(newvalue) {
        if (!newvalue || !newvalue.length) {
          this.reduction();
        } else {
          if (this.level1 === null) {
            if (this.textinfo !== await newvalue.map(item => item.name).join('/')) {
              // 我要赋值---后期赋值响应'
              this.assignment(newvalue);
            }
          }
        }
      },
      deep: true,
    },
    async mounted() {
      // 初始赋值响应
      if (this.textinfoOri && this.textinfoOri.length && this.level1 === null) {
        if (this.textinfo !== await this.selectedOptionsvalue.map(item => item.name).join('/')) {
          // 我要赋值---初始赋值响应'
          this.assignment(this.textinfoOri);
        }
      }
    },
    methods: {
      // 搜索功能
      getSearchList() {
        const selections = this.changeList();
        this.searchList = selections.filter(item => item.name && item.name.indexOf(this.searchContent) > -1);
        // 将搜索的数据选中
      },
      changeList() {
        const listInfo = JSON.parse(JSON.stringify(this.options));
        const selections = [];
        const getSelections = (arr, id, name) => {
          arr.forEach((item) => {
            item.id = id ? `${id} / ${item.id}` : String(item.id);
            item.name = name ? `${name} / ${item.name}` : String(item.name);
            selections.push({
              id: item.id.split(' / '),
              name: item.name,
              disabled: !!item.disabled,
              isSelected: !!item.isSelected,
            });
            if (item.children && item.children.length) {
              getSelections(item.children, item.id, item.name);
            }
          });
        };
        getSelections(listInfo);
        return selections;
      },
      handleSelectItem(item) {
        if (item.disabled) {
          return;
        }
        this.searchList.forEach((node) => {
          node.isSelected = false;
        });
        item.isSelected = true;
        // 抛出最外层并且执行事件
        if (item.id.length === 1) {
          this.options.forEach((node) => {
            this.treeData(node, item.id[0]);
          });
          this.performFn(this.options1, 1, String(item.id[0]));
        } else if (item.id.length === 2) {
          this.options.forEach((node) => {
            this.treeData(node, item.id[0]);
          });
          this.performFn(this.options1, 1, String(item.id[0]));
          this.options.forEach((node) => {
            this.treeData(node, item.id[1]);
          });
          this.performFn(this.options2, 2, String(item.id[1]));
        } else {
          this.options.forEach((node) => {
            this.treeData(node, item.id[0]);
          });
          this.performFn(this.options1, 1, String(item.id[0]));
          this.options.forEach((node) => {
            this.treeData(node, item.id[1]);
          });
          this.performFn(this.options2, 2, String(item.id[1]));
          this.options.forEach((node) => {
            this.treeData(node, item.id[2]);
          });
          this.performFn(this.options3, 3, String(item.id[2]));
        }
        // 关闭下拉框并清空数据
        this.selector.open = false;
        this.searchContent = '';
      },
      // 通过ID来获取当前的item项
      treeData(tree, id) {
        if (String(id) === String(tree.id)) {
          this.searchItem = tree;
        }
        if (tree.children === null || (tree.children && !tree.children.length)) {
          return;
        }
        tree.children.forEach((tree) => {
          this.treeData(tree, id);
        });
      },
      // 执行方法体
      performFn(optionsList, level, id) {
        const itemIndex = optionsList.findIndex(node => String(node.id) === String(id));
        const optionsItem = optionsList.find(node => String(node.id) === String(id));
        this.selectLevel(level, itemIndex, optionsItem);
      },
      // 从外向里赋值
      async assignment(textinfoOri) {
        await this.options1;
        for (let i = 0; i < textinfoOri.length; i++) {
          let indexPosition = -1;
          this[`options${i + 1}`].map((it, ind) => {
            if (textinfoOri[i].id === it.id) {
              indexPosition = ind;
            }
          });
          if (indexPosition !== -1) {
            await this.selectLevel(i + 1, indexPosition, textinfoOri[i]);
          }
        }
        this.selector.open = false;
      },
      closeHidden() {
        this.selector.open = false;
      },
      // 改变父model
      async fnTextinfo() {
        await this.$emit('change', this.selectedOptionsvalue);
      },
      scrollEvent($event) {
        this.styletranslateY.transform = `translate(-26px,${-$event.target.scrollTop - 32}px)`;
      },
      // 展开/关闭 级联选择器
      async showcascader() {
        if (this.disabled) {
          return;
        }
        if (!this.textinfo) {
          this.reduction();
        }
        this.selector.open = !this.selector.open;
        const el = this.$refs.cascader;
        const vm = this;
        const documentHandler = function (e) {
          if (!el.contains(e.target)) {
            vm.selector.open = false;
            vm.$root.cascaderFunction = undefined;
            document.removeEventListener('click', documentHandler);
          }
        };
        // 可以解除事件监听
        if (!this.selector.open) {
          await document.removeEventListener('click', this.$root.cascaderFunction);
          this.$root.cascaderFunction = undefined;
          return;
        }
        if (this.selector.open && !this.$root.cascaderFunction) {
          this.$root.cascaderFunction = documentHandler;
          document.addEventListener('click', documentHandler);
        }
      },
      // 设置选择项
      async settextinfo(item, type = 'own') {
        if (type === 'give_default') {
          if (item[0] && item[0].id) {
            await this.$emit('change', item);
            this.textinfo = item[0].name;
          }
          return;
        }
        if (!item.children || !item.children.length) {
          this.selector.open = false;
        }
        this.textinfo = await this.selectedOptionsvalue.map(item => item.name).join('/');
        await this.$emit('change', this.selectedOptionsvalue);
        await this.fnTextinfo();
      },
      // 选中每级目录
      async selectLevel(level, index, item) {
        if (level === 1) {
          this.level3 = null;
          this.level2 = null;
          this.level1 = index;
          this.options1.forEach((ite) => {
            ite.isselect = false;
          });
          this.options2.forEach((ite) => {
            ite.isselect = false;
          });
          this.options3.forEach((ite) => {
            ite.isselect = false;
          });
          this.options1[index].isselect = true;
          this.options3 = [];
          this.options2 = [];
          this.selectedOptionsvalue = [];
          this.options2 = item.children || [];
        } else if (level === 2) {
          this.level3 = null;
          this.level2 = index;
          this.options2.forEach((ite) => {
            ite.isselect = false;
          });
          this.options3.forEach((ite) => {
            ite.isselect = false;
          });
          this.options2[index].isselect = true;
          this.options3 = [];
          this.selectedOptionsvalue = this.selectedOptionsvalue.slice(0, 1);
          this.options3 = item.children || [];
        } else {
          this.level3 = index;
          this.options3.forEach((ite) => {
            ite.isselect = false;
          });
          this.options3[index].isselect = true;
          this.selectedOptionsvalue = this.selectedOptionsvalue.slice(0, 2);
        }
        this.selectedOptionsvalue.push(item);
        // 每一级选不关闭
        if (item.key !== 'favorites') {
          this.settextinfo(item);
        }
      },
      // 收藏
      async collect_s(item) {
        const objdata = Object.assign({}, item);
        // 数据还原
        if (objdata.isselect) {
          delete objdata.isselect;
        }
        if (objdata.favorites) {
          delete objdata.favorites;
        }
        const index = this.options_favorites_sign.indexOf(objdata.key);
        if (index !== -1) {
          await this.cancelcollect_s(item, index);
          return;
        }
        // 收藏
        await this.$emit('collect', [...this.optionsFavorites, objdata]);
      },
      // 取消收藏
      async cancelcollect_s(item, index) {
        if (item.isselect) {
          this.textinfo = '';
        }
        const objdata = Object.assign({}, item);
        if (objdata.isselect) {
          delete objdata.isselect;
        }
        if (objdata.favorites) {
          delete objdata.favorites;
        }
        const favoriteslist = [...this.optionsFavorites];
        favoriteslist.splice(index, 1);
        // 取消收藏
        await this.$emit('cancelcollect', favoriteslist);
      },
      async reduction() {
        this.textinfo = '';
        this.isCollectOpen = true;
        this.level3 = null;
        this.level2 = null;
        this.level1 = null;
        this.options1.forEach((ite) => {
          ite.isselect = false;
        });
        this.options2.forEach((ite) => {
          ite.isselect = false;
        });
        this.options3.forEach((ite) => {
          ite.isselect = false;
        });
        this.options3 = [];
        this.options2 = [];
        this.selectedOptionsvalue = [];
      },
    },
    create() {
    },
  };
</script>

<style scoped lang='scss'>
    @import '../../../scss/mixins/scroller.scss';

    .bk-itsm-cascader {
        position: relative;
        width: 100%;
        height: 32px;
        overflow: hidden;

        .bk-cascader {
            height: 100%;
        }

        .bk-cascader-input {
            input {
                cursor: pointer;
                height: 100%;
                width: 100%;
                border-radius: 2px;
                border: 1px solid #c3cdd7;
                padding: 0 32px 0 10px;

                &.placeholder {
                    color: #c3cdd7;
                    font-size: 14px;
                }

                &.fill {
                    color: #666;
                }
            }

            input.focus,
            input:focus {
                // color: #c3cdd7;
                border-color: #409EFF;
            }

            input[disabled='disabled'].disabled {
                color: #aaa;
                cursor: not-allowed;
                background: #fafafa;
            }

        }

        .bk-cascader-select {
            box-shadow: 0px 0px 7px rgba(0, 0, 0, 0.1);
            height: 200px;
            position: absolute;
            min-width: 160px;
            width: auto;
            margin-top: 32px;
            display: flex;
            z-index: 200;
            background: white;
            border-left: 1px solid #DDE4EB;

            ul.bk-select {
                border-left: 1px solid #DDE4EB;
                padding: 5px 0;
                height: 100%;
                overflow: auto;
                @include scroller;
                min-width: 160px;

                li {
                    font-size: 14px;
                    // padding: 8px 0px;
                    // position: relative !important;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    color: #606266;
                    height: 34px;
                    line-height: 1.5;
                    box-sizing: border-box;
                    outline: none;

                    cursor: pointer;
                    display: flex;

                    & > span {
                        line-height: 34px;
                    }

                    span.bk-info-left {
                        text-align: left;
                        flex: 1;
                        padding-left: 15px;

                        &.signcolor {
                            color: #3E86FF;
                        }

                        &.bkCollect {
                            // color: #313238;
                        }
                    }

                    span.bk-info-right {
                        // display: inline-block;
                        text-align: right;
                        visibility: hidden;
                        padding-right: 10px;

                        &.signcolor,
                        &.iconinfo {
                            visibility: visible;
                        }

                        & > i {
                            line-height: 34px;
                            color: #C3CDD7;
                            font-size: 22px;
                        }

                        &.collect {
                            display: flex;
                            // position: relative;
                        }

                        // &.collect::after{
                        //     position: absolute;
                        //     content: '1111';
                        //     // width: 640px;
                        //     // height: 40px;
                        //     // left: 0;
                        //     // bottom: -40px;
                        // }
                        .bk-tip-info.bk-change {
                            position: fixed;
                            visibility: hidden;
                            color: #fff;
                            background: #333;
                            border-color: #333;
                            padding: 6px 8px;
                            margin: 0;
                            font-size: 12px;
                            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
                            border: 1px solid #d9d9d9;
                            border-radius: 4px;
                            transform: translate3d(0, 0, 0);
                            transition: opacity .3s;
                            will-change: opacity, transform;
                            -webkit-font-smoothing: subpixel-antialiased;
                            line-height: 24px;

                            .bk-tooltips-arrows {
                                border-width: 8px;
                                top: 97%;
                                left: 50%;
                                transform: translate(-50%, 0);
                                position: absolute;
                                z-index: -1;
                                width: 0;
                                height: 0;
                                padding: 0;
                                margin: 0;
                                border-color: transparent;
                                border-style: inherit;
                                display: inline-block;
                                border-top-color: #333;
                            }
                        }

                        &:hover {
                            .bk-tip-info.bk-change {
                                visibility: visible;
                            }
                        }

                    }

                    &:hover {
                        background: #EBF4FF;

                        span.bk-info-right {
                            // display: inline-block;
                            visibility: visible;
                            width: auto;
                        }
                    }
                }
            }

            ul.bk-select-one {
                border-left: 0;
            }
        }

        &.visible {
            overflow: visible;
        }
    }
    .bk-selector-icon {
        position: absolute;
        top: 5px;
        right: 2px;
        font-size: 22px;
        color: #979ba5;
        -webkit-transition: all .2s linear;
        transition: all .2s linear;
        cursor: pointer;
    }

    .bk-cascade-panel {
        height: 200px;
        padding: 5px 0;
        color: #63656e;
        position: absolute;
        top: 32px;
        left: 0;
        border: 1px solid #c3cdd7;
        width: 100%;
        background: #fff;
        z-index: 2;
        .bk-cascade-panel-ul {
            float: left;
            height: 100%;
            padding: 0;
            margin: 0;
            margin-top: 26px;
            border-top: 1px solid #c3cdd7;
            list-style: none;
            overflow-y: auto;
            @include scroller;
        }
        .bk-cascade-border {
            border-right: 1px solid #c4c6cc;
        }
        .bk-option {
            position: relative;
            .bk-cascade-right {
                position: absolute;
                top: 11px;
                right: 10px;
            }
        }
        .is-multiple {
            background-color: #fff!important;
        }
        .bk-option-none {
            margin-top: 12px;
            padding: 0 10px;
            font-size: 12px;
            line-height: 32px;
        }
    }
    .bk-search-input {
        height: 32px;
        width: 100%;
        padding: 0 10px;
        position: absolute;
        top: 32px;
        left: 0;
        border-right: 1px solid #c4c6cc;
        border-left: 1px solid #c4c6cc;
        background-color: #fff;
        z-index: 5;
    }
    .bk-search-input-one {
        width: 161px;
    }
    .bk-search-input-two {
        width: 321px;
    }
    .bk-search-input-three {
        width: 481px;
    }
    .bk-cascade-search-input {
        width: 100%;
        height: 32px;
        border: none;
        font-size: 12px;
        outline: 0;
        cursor: text;
    }
    .bk-other-search {
        border: none;
        top: 5px;
    }
    .bk-option {
        position: relative;
        cursor: pointer;
        &:hover,
        &.is-highlight {
            color: #3a84ff;
            background-color: #eaf3ff;
        }
        &.is-disabled {
            color: #c4c6cc;
            cursor: not-allowed;
            background-color: #fff;
        }
        &.is-selected {
            color: #3a84ff;
            background-color: #f4f6fa;
        }
        &.is-selected.is-disabled {
            background-color: #fff;
            color: #c4c6cc;
            .bk-option-icon {
                color: #c4c6cc;
            }
        }
    }
    .bk-option-content {
        position: relative;
        padding: 0 16px;
        .bk-option-content-default {
            padding: 0 20px 0 0;
            font-size: 0;
        }
        .bk-option-name {
            display: inline-block;
            vertical-align: middle;
            font-size: 12px;
        }
        .bk-option-icon {
            position: absolute;
            right: 12px;
            top: 12px;
            color: #3a84ff;
            font-size: 12px;
            font-weight: bold;
        }
    }
</style>
