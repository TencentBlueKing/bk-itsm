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
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :desc="item.tips" desc-type="icon">
      <div style="position: relative;">
        <div class="bk-form-content" style="position: relative;">
          <custom-upload
            ref="upload"
            :name="'field_file'"
            :multiple="true"
            :with-credentials="true"
            :disabled="disabled"
            @on-success="uploadSuccess"
            @on-error="uploadErr"
            @on-progress="uploadProgress"
            @on-done="uploadDone"
            :tip="''"
            :size="200"
            :url="url">
          </custom-upload>
          <ul>
            <li v-for="(file, index) in datas"
              class="upload_p"
              v-show="!file.errorMsg"
              style="word-break: break-word;"
              :key="index">
              <span>{{file.name}}</span>
              <span style="color: #3c96ff; margin-left: 10px; cursor: pointer"
                @click="deleteFile(file)"
                class="bk-icon icon-delete">
              </span>
            </li>
          </ul>
        </div>
      </div>
      <div class="bk-form-item" v-if="tempFileList.length > 0">
        <label class="bk-label">{{ $t('m.newCommon["模板下载"]') }}：</label>
        <div class="bk-form-content">
          <ul v-for="(file, index) in tempFileList" :key="index">
            <li @click="downloadFile(file)"
              class="bk-icon icon-download bk-tab-cursor fa-file"> {{file.name}}
            </li>
          </ul>
        </div>
      </div>
      <template v-if="item.checkValue">
        <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
        <p class="bk-task-error" v-else>{{ item.name }}{{$t('m.newCommon["为必填项！"]')}}</p>
      </template>
    </bk-form-item>
  </div>
</template>

<script>
  import customUpload from '../customUpload/upload';

  export default {
    name: 'FILE',
    components: {
      customUpload,
    },
    props: {
      item: {
        type: Object,
        required: true,
        default: () => {
        },
      },
      idInfo: {
        type: Object,
        required: false,
        default: () => null,
      },
      isCurrent: {
        type: Boolean,
        default: false,
      },
      isFilePreview: {
        type: Boolean,
        default: false,
      },
      isBuild: {
        type: Boolean,
        default: false,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        datas: [],
        uploadFileList: [],
        tempFileList: [],
        historyList: [],
        url: this.isFilePreview ? '' : `${window.SITE_URL}api/misc/upload_file/`,
        // downloadUrl: window.site + `workflow/fields/`,
        // 记录上传文件值
        tempObj: {},
      };
    },
    mounted() {
      this.item.val = [];
      this.choiceToList();
    },
    methods: {
      choiceToList() {
        for (const key in this.item.choice) {
          this.tempFileList.push({ ...this.item.choice[key], key });
        }
        if (this.item.value) {
          const tempObj = JSON.parse(this.item.value);
          for (const key in tempObj) {
            this.historyList.push({ ...tempObj[key], key });
          }
          this.datas = this.historyList.concat([]);
          this.item.val = '';
          const valueList = [];
          this.datas.forEach((node) => {
            const nodeValue = {};
            nodeValue[node.key] = {
              path: node.path,
              name: node.name,
            };
            valueList.push(JSON.stringify(nodeValue));
          });
          this.item.val = valueList.join(',');
        }
      },
      // 修改 附件优化 1031
      downloadFile(file) {
        const tempKey = file.key;
        if (this.isBuild) {
          window.open(`${window.SITE_URL
          }api/ticket/fields/${this.item.id}/download_file/?unique_key=${tempKey}&file_type=version&flow_id=${this.item.version_id}`);
        } else if (this.isCurrent) {
          window.open(`${window.SITE_URL
          }api/ticket/fields/${this.item.id}/download_file/?unique_key=${tempKey}&file_type=template`);
        } else {
          window.open(`${window.SITE_URL
          }api/workflow/fields/${this.item.id}/download_file/?unique_key=${tempKey}&file_type=template`);
        }
      },
      uploadErr() {
        // ...
      },
      // 修改 附件优化 1031
      uploadSuccess(fileList) {
        this.datas = fileList;
        this.uploadFileList = fileList;
        this.item.value = '';
        this.item.val = this.item.value;
        fileList.forEach((it) => {
          if ((!it.errorMsg) && it.responseData.data) {
            for (const key in it.responseData.data.succeed_files) {
              this.$set(this.tempObj, key, it.responseData.data.succeed_files[key]);
            }
          }
        });
        // 如果存在历史数据则将历史数据保存
        if (this.historyList.length) {
          this.datas = this.datas.concat(this.historyList);
          this.historyList.forEach((node) => {
            this.tempObj[node.key] = {
              path: node.path,
              name: node.name,
            };
          });
        }
        this.item.value = JSON.stringify(this.tempObj);
        this.item.val = this.item.value;
      },
      // 修改 附件优化 1031
      uploadProgress() {
        this.$store.commit('changeFileStatus', true);
      },
      uploadDone() {
        this.$store.commit('changeFileStatus', false);
      },
      // 修改 附件优化 1031
      deleteFile(file) {
        this.datas.splice(this.datas.indexOf(file), 1);
        // 如果删除的是历史数据，则将对于的历史数据清空
        if (this.historyList.length && this.historyList.some(node => node.key === file.key)) {
          this.historyList = this.historyList.filter(node => node.key !== file.key);
          for (const key in this.tempObj) {
            if (key === file.key) {
              delete this.tempObj[key];
            }
          }
        } else {
          for (const key in this.tempObj) {
            for (const fileKey in file.responseData.data.succeed_files) {
              if (key === fileKey) {
                delete this.tempObj[key];
              }
            }
          }
        }
        // 删除附件的时候也应该清空upload内的数据
        const fileIndex = this.uploadFileList.indexOf(file);
        if (fileIndex !== -1) {
          this.$refs.upload.deleteFile(fileIndex, file);
        }
        if (!Object.keys(this.tempObj).length) {
          this.item.val = '';
        } else {
          this.item.val = JSON.stringify(this.tempObj);
        }
      },
    },
  };
</script>

<style lang='scss' scoped>

    li.fa-file {
        margin-bottom: 2px;
        color: #3c96ff;
        cursor: pointer;
        width: auto;
        float: left;
        font-size: 14px;
        padding: 10px 30px 0px 0px
    }

    .upload_p {
        line-height: 30px;
        color: #737987;
        font-size: 14px;
        font-weight: bold;
    }
</style>
