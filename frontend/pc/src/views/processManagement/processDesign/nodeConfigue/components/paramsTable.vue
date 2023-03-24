<template>
  <div>
    <bk-table :data="list" :disabled="true">
      <bk-table-column width="40">
        <template slot-scope="props">
          <bk-checkbox v-model="props.row.select" :disabled="disable"></bk-checkbox>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m['字段名']`)" :render-header="$renderHeader">
        <template slot-scope="props">
          <bk-input :behavior="'simplicity'"
            :disabled="disable"
            v-model="props.row.key"
            @change="changeInput(props.row, props.$index)"></bk-input>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m['值']`)" :render-header="$renderHeader">
        <template slot-scope="props">
          <bk-input style="z-index: 101"
            v-model="props.row.value"
            :behavior="'simplicity'"
            :disabled="disable"
            :placeholder="isStatus ? $t(`m['输入“{{”可选择引用变量']`) : $t(`m['请输入']`)"
            @change="changeInput(props.row, props.$index)"></bk-input>
          <bk-popover
            v-if="isStatus"
            :ref="`inputParam${props.$index}`"
            placement="bottom"
            theme="light"
            :arrow="false"
            :always="!props.row.value"
            :disabled="!props.row.value"
            :ext-cls="props.row.value ? 'show-tippy' : ''"
            :transfer="true">
            <div slot="content" class="params-select-value">
              <ul class="params-select">
                <li v-for="(item, index) in wwwFormData"
                  :key="index"
                  @click="handleSelectContent(item)">
                  {{item.name}}
                  <span class="variable-key">({{item.key}})</span>
                </li>
              </ul>
            </div>
          </bk-popover>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m['描述']`)" :render-header="$renderHeader">
        <template slot-scope="props">
          <bk-input
            :behavior="'simplicity'"
            :disabled="disable"
            v-model="props.row.desc"
            @change="changeInput(props.row, props.$index)"></bk-input>
        </template>
      </bk-table-column>
      <bk-table-column width="40">
        <template slot-scope="props" v-if="isShowDelete !== list.indexOf(props.row)">
          <i v-if="!disable" class="bk-itsm-icon icon-itsm-icon-three-one" @click="handleDelete(props.row)"></i>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
  export default {
    name: 'paramsTable',
    props: {
      list: {
        type: Array,
        defalut: () => [],
      },
      disable: {
        type: Boolean,
        default() {
          return false;
        },
      },
      stateList: Array,
      isStatus: {
        type: Boolean,
        default() {
          return true;
        },
      },
    },
    data() {
      return {
        formData: [],
        wwwFormData: [],
        curCulum: '',
        curIndex: '',
        filterParams: '',
      };
    },
    computed: {
      isShowDelete() {
        return this.list.length - 1;
      },
      isShowSelect() {
        return this.wwwFormData.length === 0 || this.filterParams === '';
      },
    },
    watch: {
      list: {
        handler(val) {
          if (this.isStatus) {
            val.forEach((item, index) => {
              if (item.value === '') {
                this.$nextTick(() => {
                  this.$refs[`inputParam${index}`].hideHandler();
                });
              }
            });
          }
        },
        immediate: true,
        deep: true,
      },
      wwwFormData: {
        handler(val) {
          if (val.length === 0 && this.isStatus) {
            for (let index = 0; index < this.list.length; index++) {
              this.$nextTick(() => {
                this.$refs[`inputParam${index}`].hideHandler();
              });
            }
          }
        },
        immediate: true,
      },
    },
    mounted() {
      if (this.list.length !== 0 && this.isStatus) {
        for (let index = 0; index < this.list.length; index++) {
          this.$nextTick(() => {
            this.$refs[`inputParam${index}`].hideHandler();
          });
        }
      }
    },
    methods: {
      changeTab(item) {
        this.acticeTab = item.key;
      },
      handleDelete(row) {
        const index = this.list.indexOf(row);
        if (index !== -1) {
          this.list.splice(index, 1);
        }
      },
      handleSelectContent(item) {
        this.list[this.curIndex].value = `${this.list[this.curIndex].value.slice(0, -(this.filterParams.length + 2))}{{ ${item.key}}}`;
        this.$refs[`inputParam${this.curIndex}`].hideHandler();
        this.filterParams = '';
        this.wwwFormData = [];
      },
      changeInput(item, rowIndex) {
        if (this.isStatus) {
          const index = item.value.lastIndexOf('\{\{');
          this.curIndex = '';
          if (index !== -1) {
            this.$refs[`inputParam${rowIndex}`].showHandler();
            const params = item.value.substring(index + 2, item.value.length) || '';
            this.filterParams = !params ? '' : params;
            this.wwwFormData = this.stateList.filter(ite => ite.name.indexOf(this.filterParams) !== -1 || ite.key.indexOf(this.filterParams) !== -1);
            this.curIndex = rowIndex;
          } else {
            this.$refs[`inputParam${rowIndex}`].hideHandler();
          }
          this.curCulum = item;
        }
        // 输入清除error
        this.$emit('changeFormStatus', false);
        if (!item.check) {
          item.check = true;
          item.select = true;
          this.list.push({
            check: false,
            key: '',
            value: '',
            desc: '',
            select: false,
          });
        } else {
          const { key, value, desc } = item;
          const checkList = [key, value, desc];
          if (checkList.every(item => item === '')) {
            this.list.pop();
            item.check = false;
            item.select = false;
          }
        }
      },
    },
  };
</script>

<style lang='scss' scoped>
@import '../../../../../scss/mixins/scroller.scss';
.icon-itsm-icon-three-one {
    font-size: 16px;
    cursor: pointer;
}
.params-select-value {
    width: 200px;
    height: 200px;
    // padding: 0;
}
.params-select {
    position: absolute;
    background-color: #fff;
    // border: 1px solid #c4c6cc;
    border-radius: 4px;
    font-size: 12px;
    z-index: 100;
    width: 200px;
    height: 200px;
    overflow: auto;
    @include scroller;
    li {
        width: 300px;
        height: 30px;
        line-height: 30px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        cursor: pointer;
        color: #75777f;
        &:hover {
            background-color: #e1ecff;
            color: #3a84ff;
        }
        span {
            font-size: 12px;
        }
    }
}
/deep/ .tippy-tooltip {
    padding: 0;
}
/deep/ .tippy-arrow {
    display: none;
}
/deep/ .bk-tooltip {
    display: block;
    .bk-tooltip-ref {
        display: block;
    }
}
.show-tippy {
    z-index: 1000;
    display: none;
}
.var-group {
    width: 100%;
    height: 100%;
    position: relative;
    .select-custom {
        width: 100%;
        visibility: hidden;
        position: absolute;
        top: 0;
        left: 0;
    }
}
</style>
