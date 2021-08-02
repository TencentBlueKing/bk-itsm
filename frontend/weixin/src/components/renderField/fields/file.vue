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
  <div class="field-file">
    <label class="ui-field-label">{{ item.name }}</label>
    <div v-if="!isViewMode" class="uploader-wrap">
      <van-uploader
        :key="updateKey"
        v-model="fileList"
        preview-size="80px"
        upload-icon="add-o"
        :multiple="true"
        :max-size="200 * 1024 * 1024"
        accept=".txt,.log,.pdf,.doc,.ppt,.xls,.docx,.pptx,.xlsx,.zip,.jpg,.png"
        :after-read="afterRead" />
    </div>
    <ul v-else class="upload-list">
      <li
        v-for="(file, index) in uploadList"
        :key="index"
        class="upload-item">
        {{ file.name }}
        <span class="down-icon" @click="handleDownFileClick(file)"><van-icon name="down" /></span>
      </li>
      <li v-if="!uploadList.length" class="upload-item">无</li>
    </ul>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, ref, toRefs, watch } from 'vue'

export type TSucceedFiles = Record<string, { name: string, path: string }>

export type TFile = { key: string; name: string; path: string }

export interface IFileObj {
  content: string;
  file: any;
  message: string;
  status: 'done' | 'uploading' | 'failed';
  // eslint-disable-next-line camelcase
  succeed_files?: TSucceedFiles
}

export default defineComponent({
  name: 'FieldFile',
  props: {
    item: {
      type: Object,
      default: () => ({})
    },
    isViewMode: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'change'
  ],
  setup(props, { emit }) {
    const { item } =  toRefs<{ item: any }>(props)

    const fileList = ref<IFileObj []>([]) // 已上传的文件列表（失败+成功）
    const updateKey = ref<number>(1010) // 更新组件 key
    const val = ref<string>('')
    const originValue = computed(() => item.value.value || '{}')

    val.value = originValue.value
    watch(originValue, (val) => {
      val.value = val.value
    })
    // value change
    watch(val, (val) => {
      emit('change', val)
    })

    // 已经成功上传的文件列表
    const uploadList = computed(() => {
      const list: TFile [] = []
      const allSucceedFiles = JSON.parse(val.value)
      Object.keys(allSucceedFiles).forEach((key: string) => {
        list.push({
          key,
          ...allSucceedFiles[key]
        })
      })
      return list
    })

    // 手动更新组件
    const updateComponent = () => {
      updateKey.value = new Date().getTime()

      const allSucceedFiles = fileList.value.reduce((all: TSucceedFiles, file: IFileObj) => {
        if (file.status === 'done') {
          // eslint-disable-next-line no-param-reassign
          all = { ...all, ...file.succeed_files }
        }
        return all
      }, {})
      val.value = JSON.stringify(allSucceedFiles)
    }

    // 读取文件后
    const afterRead = (fileObj: any): void => {
      console.log(fileObj, 'filefilefilefile')
      fileObj.status = 'uploading'
      fileObj.message = '上传中...'
      uploadFile(fileObj)
    }

    // 上传
    const uploadFile = (fileObj: any) => {
      const formData = new FormData()
      const xhr = new XMLHttpRequest()
      const { name } = fileObj.file
      formData.append(name, fileObj.file)

      xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
          try {
            const response = JSON.parse(xhr.responseText)
            if (xhr.status === 200) {
              fileObj.status = 'done'
              fileObj.succeed_files = response.data.succeed_files
            } else {
              fileObj.status = 'failed'
              fileObj.message = '失败'
              console.error(response.message)
            }
          } catch (error) {
            fileObj.status = 'failed'
            fileObj.message = error.message
            console.error(error.message)
          } finally {
            updateComponent()
          }
        }
      }
      xhr.withCredentials = true
      xhr.open('POST', `${(window as any).SITE_URL}weixin/api/misc/upload_file/`, true)
      xhr.send(formData)
    }

    // 下载附件
    const handleDownFileClick = (file: TFile) => {
      const downFileUrl =  `${(window as any).SITE_URL}weixin/api/ticket/fields/${item.value.id}/download_file/?unique_key=${file.key}&file_type=ticket`
      window.open(downFileUrl)
    }

    // 校验
    const validate = (): boolean => !!val.value && val.value !== '{}'

    return {
      val,
      // eslint-disable-next-line vue/no-dupe-keys
      item,
      validate,
      afterRead,
      fileList,
      updateKey,
      uploadList,
      originValue,
      handleDownFileClick
    }
  }
})
</script>
<style lang="postcss">
  .van-uploader__preview-delete {
    width: 5vw;
    height: 5vw;
    .van-uploader__preview-delete-icon {
      font-size: 5vw;
    }
  }
  .van-uploader__upload .van-uploader__upload-icon {
    font-size: 5vw;
  }
  .field-file {
    padding: 24px 0;
    .ui-field-label {
      display: block;
      color: #323233;
      font-size: 24px;
    }
    .uploader-wrap {
      margin: 20px;
    }
  }

  .upload-list {
    padding: 0 24px;
    .upload-item {
      line-height: 42px;
      font-size: 24px;
      color: #323233;
      font-weight: normal;
      .down-icon {
        color: #3a84ff;
        vertical-align: middle;
      }
    }
  }
</style>
