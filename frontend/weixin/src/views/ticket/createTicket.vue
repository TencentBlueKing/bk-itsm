<template>
  <div class="create-ticket">
    <div v-if="!isCreated" class="created-page">
      <section class="create-header">
        <div class="create-container">
          <div class="create-icon">
            <i class="itsm-mobile-icon icon-tidanxiangqing"></i>
          </div>
          <div class="header-content">
            <h3 class="service-title">
              <span class="service-name">{{ service.info.name }}</span>
              <i
                :class="['itsm-mobile-icon', service.info.favorite ? 'icon-favorite orange': 'icon-favorite-o']"
                @click="onChangeFavorite(service.info)">
              </i>
            </h3>
            <pre class="service-desc">{{ service.info.desc || '暂无备注' }}</pre>
          </div>
        </div>
      </section>
      <section class="field-content">
        <render-field
          ref="renderField"
          :fields="fieldList">
        </render-field>
      </section>
      <section class="ticket-opera">
        <div class="attention">
          <van-checkbox
            v-model="attention"
            shape="square">
            关注此单据，单据更新时通知我
          </van-checkbox>
        </div>
        <div class="opera-btn">
          <van-button
            class="btn"
            type="default"
            size="small"
            @click="$router.go(-1)">
            取消
          </van-button>
          <van-button
            class="btn"
            type="primary"
            :disabled="submitDisabled"
            @click="onCreateSubmit">
            提交
          </van-button>
        </div>
      </section>
    </div>
    <div v-else class="created-success">
      <div class="sucess-icon itsm-mobile-icon icon-chenggong"></div>
      <h2 class="result">提单成功</h2>
      <p class="tip">当前流程已经跳转至下一节点，您可以选择</p>
      <div class="operate">
        <van-button
          class="btn"
          type="default"
          size="small"
          @click="$router.push({ name: 'homeDefault' })">
          返回首页
        </van-button>
        <van-button
          class="btn"
          type="primary"
          size="small"
          @click="onViewTicketDetail">
          查看单据详情
        </van-button>
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { onMounted, ref, defineComponent, reactive, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import RenderField from '../../components/renderField/index.vue'
import { IServiceInfo } from '../../typings/ticket'
interface Iservice {
  info: IServiceInfo | object,
  createdId: string | number,
  createdSn: string
}
const notSupportTypes: string [] = [
  'CUSTOMTABLE', // 自定义表格
  'TREESELECT', //  树形选择
  // 'FILE', //        文件上传
  'CASCADE', //     级联字段
  'SOPS_TEMPLATE', // 标准运维
  'TABLE' //         表格 TODO
]
export default defineComponent({
  name: 'createTicket',
  components: {
    RenderField
  },
  props: {},
  emits: {},
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()

    const fieldList = ref<Array<any>>([])
    const attention = ref<boolean>(false)
    const isCreated = ref<boolean>(false)
    const renderField = ref(null)
    const service = reactive<Iservice>({
      info: {},
      createdId: '',
      createdSn: ''
    })
    const getSubmitFields = async () => {
      const res = await store.dispatch('ticket/getSubmitFields', {
        service_id: route.query.serviceId
      })
      fieldList.value = res.result ? res.data : []
    }
    const getServiceDetail = async () => {
      const res = await store.dispatch('ticket/getServiceDetail', Number(route.query.serviceId))
      if (res.data) {
        service.info = res.data
      }
    }
    const getPriorityDisabled = ref<boolean>(true)
    const submitDisabled = ref<boolean>(true)
    watch(fieldList, (val) => {
      getPriorityDisabled.value = true
      // 提交禁用按钮
      submitDisabled.value = !val.filter(sup => !notSupportTypes.includes(sup.type) && sup.validate_type === 'REQUIRE').every(item => item.value !== '')
      // 当前需要依赖条件的字段列表
      const currentApiFields = val.filter(ite => (ite.source_type === 'API' || ite.key === 'priority')
        && ite.related_fields && ite.related_fields.rely_on
        && ite.related_fields.rely_on.length)
      // 当前字段列表所需要依赖字段的类型
      let relyOnFieldsKeyList = []
      currentApiFields.forEach((ite) => {
        relyOnFieldsKeyList = [...ite.related_fields.rely_on]
      })
      // 当前字段所需要依赖项
      const CurrentreBeReliedFields = val.filter(ite => ite.related_fields && ite.related_fields.be_relied
        && ite.related_fields.be_relied.length)
      // 当前字段列表所需要依赖的字段
      const currentrelyOnFields = CurrentreBeReliedFields
        .filter(ite => relyOnFieldsKeyList.indexOf(ite.key) !== -1)

      currentrelyOnFields.forEach(ite => {
        const rca = currentApiFields.filter(item_ => item_.related_fields.rely_on.indexOf(ite.key) !== -1)
        rca.forEach(async (itemRelate) => {
          const relateCurrentreBeRelied = currentrelyOnFields
            .filter(itemRe => itemRelate.related_fields.rely_on.indexOf(itemRe.key) !== -1)
          const isALlFill = relateCurrentreBeRelied.every(itemRely => itemRely.val)
          if (isALlFill && getPriorityDisabled.value) {
            getPriorityDisabled.value = false
            const params = {
              id: itemRelate.id,
              api_instance_id: itemRelate.api_instance_id,
              kv_relation: itemRelate.kv_relation
            }
            getPriority(params, itemRelate, isALlFill, currentrelyOnFields)
          }
        })
      })
    }, { deep: true })
    const getPriority = async (params: any, item: any, isALlFill: boolean, currentrelyOnFields: any): void => {
      const data = JSON.parse(JSON.stringify(params))
      data.service_type = item.service || service.info.key
      delete data.id
      item.allFill = isALlFill
      currentrelyOnFields.forEach((i: any) => {
        data[i.key] = i.value
      })
      store.dispatch('get_priority', data).then((res) => {
        item.val = res
        item.value = res
      })
    }
    const onCreateSubmit = async () => {
      const { catalog_id, id, bounded_catalogs } = service.info
      const params = {
        catalog_id,
        service_id: id,
        service_type: bounded_catalogs[0],
        fields: [],
        creator: window.username,
        attention: attention.value
      }
      fieldList.value.forEach(item => {
        const showField = item.showFeild || item.showField
        params.fields.push({
          type: item.type,
          id: item.id,
          key: item.key,
          value: showField ? item.value : '',
          choice: item.choice
        })
      })
      const res = await store.dispatch('ticket/createTicketSubmit', params)
      if (res.result) {
        isCreated.value = true
        service.createdId = res.data.id
        service.createdSn = res.data.sn
      }
    }
    const onViewTicketDetail = (): void => {
      router.push({
        name: 'ticket',
        params: {
          id: service.createdId
        }
      })
    }
    const onChangeFavorite = (service: any): void => {
      store.dispatch('toggleServiceFavorite', {
        id: service.id,
        favorite: !service.favorite
      }).then(res => {
        if (res.result) {
          service.favorite = !service.favorite
        }
      })
    }
    onMounted(() => {
      getServiceDetail()
      getSubmitFields()
    })
    return {
      service,
      isCreated,
      attention,
      renderField,
      submitDisabled,
      fieldList,
      onCreateSubmit,
      getServiceDetail,
      onViewTicketDetail,
      onChangeFavorite
    }
  }
})
</script>

<style lang="postcss" scoped>
.orange {
  color: #fbb948;
}
.create-ticket {
  width: 100%;
  height: 100%;
  position: relative;
  .created-page {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    .create-header {
      width: 100%;
      background-color: #f5f7fa;
      .create-container {
        background-color: #ffffff;
        margin: 40px;
        padding: 40px;
        display: flex;
        .create-icon {
          width: 100px;
          display: block;
          height: 100px;
          line-height: 100px;
          border-radius: 50%;
          text-align: center;
          font-size: 40px;
          color: #3a84ff;
          background: #e1ecff;
          margin-right: 20px;
        }
        .header-content {
          .service-title {
            height: 40px;
            line-height: 40px;
            margin-bottom: 10px;
            .service-name {
              font-weight: normal;
              color: #343538;
            }
            i {
              font-size: 40px;
              margin-left: 20px;
            }
          }
          .service-desc {
            word-break: break-all;
            white-space: normal;
            color: #9c9da7;
          }
        }
      }
    }
    .field-content {
      flex: 1;
      padding: 0 40px;
    }
    .ticket-opera {
      padding: 40px;
      .attention {
        font-size: 28px;
        margin: 20px 0;
      }
      .opera-btn {
        margin-top: 40px;
        width: 100%;
        display: flex;
        justify-content: space-between;
        .btn {
          width: 46%;
          height: 80px;
        }
      }
    }
  }
  .created-success {
    height: 50%;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    position:absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    margin: auto;
    .sucess-icon {
      color: #2ecb55;
      font-size: 140px;
    }
    .result {
      margin: 30px 0;
    }
    .tip {
      font-size: 28px;
      margin-bottom: 50px;
      color: #6a6b73;
    }
    .operate {
      width: 100%;
      display: flex;
      justify-content: center;
      .btn {
        width: 46%;
        height: 80px;
        margin: 0 10px;
      }
    }
  }
}
</style>
