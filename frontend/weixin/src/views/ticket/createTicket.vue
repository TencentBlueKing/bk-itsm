<template>
  <div class="create-ticket">
    <div v-if="!isCreated" class="created-page">
      <section class="create-header">
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
      </section>
      <section class="field-content">
        <render-field
        ref="renderField"
        :fields="fieldList"></render-field>
      </section>
      <section>
        <div class="attention">
          <van-checkbox
            v-model="attention"
            shape="square">
            关注此单据，单据更新时通知我
          </van-checkbox>
        </div>
        <van-button
          class="btn"
          type="primary"
          style="margin-right: 20px"
          :disabled="submitDisabled"
          @click="onCreateSubmit">
          提交
        </van-button>
        <van-button
          class="btn"
          type="default"
          size="small"
          @click="$router.go(-1)">
          取消
        </van-button>
      </section>
    </div>
    <div v-else class="created-sucess">
      <van-icon class="sucess-icon" name="checked" />
      <h2 class="result">提单成功</h2>
      <p class="tip">当前流程已经跳转至下一节点，现在您可以选择</p>
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
interface Iservice {
  info: object,
  createdId: string | number,
  createdSn: string
}
// interface Ifield {
//   type: string,
//   id: number,
//   key: string,
//   value: string | number,
//   choice: string
// }
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
    const submitDisabled = ref<boolean>(true)
    watch(fieldList, (val) => {
      submitDisabled.value = !val.every(item => item.value !== '')
    }, { deep: true })
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
        params.fields.push({
          type: item.type,
          id: item.id,
          key: item.key,
          value: item.showFeild ? item.value : '',
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
  padding: 20px;
  position: relative;
  .created-page {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    .create-header {
      border: 1px solid #dadada;
      padding: 20px;
      display: flex;
      .create-icon {
        width: 80px;
        display: block;
        height: 80px;
        line-height: 80px;
        border-radius: 50%;
        text-align: center;
        font-size: 40px;
        color: #3a84ff;
        background: #e1ecff;
        margin-right: 20px;
      }
      .header-content {
        flex: 1;
        .service-title {
          height: 40px;
          line-height: 40px;
          margin-bottom: 10px;
          i {
            font-size: 40px;
            margin-left: 10px;
          }
        }
        .service-desc {
          word-break: break-all;
          white-space: normal;
        }
      }
    }
    .field-content {
      flex: 1;
    }
    .attention {
      font-size: 28px;
      margin: 20px 0;
    }
    .btn {
      width: 120px;
      height: 60px;
      margin-right: 10px;
    }
    .created-sucess {
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
        color: #8ef286;
        font-size: 200px;
      }
      .result {
        margin: 24px 0;
      }
      .tip {
        font-size: 28px;
        margin-bottom: 40px;
      }
      .operate {
        width: 100%;
        display: flex;
        justify-content: center;
        .btn {
          width: 200px;
          height: 60px;
          margin: 0 10px;
        }
      }
    }
  }
}
</style>
