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
  <div class="message-card">
    <div class="info-content van-hairline--bottom">
      <h5>{{ ticketDetail.title }}</h5>
      <div class="info-sn">
        <span
          class="ticket-status"
          :style="getStatusColor(ticketDetail)">
          {{ ticketDetail.current_status_display }}
        </span>
        {{ ticketDetail.sn }} | 提单人 ：{{ ticketDetail.creator }}
      </div>
      <p>服务 ：{{ ticketDetail.catalog_fullname }} > {{ ticketDetail.service_name }}</p>
      <p>提单时间 ：{{ ticketDetail.create_at }}</p>
      <div class="info-effect">
        <div class="effect-btn">
          <van-button
            v-if="ticketDetail.can_withdraw"
            class="revoke-btn"
            @click="onRevokeClick(ticketDetail.id)">
            <i class="itsm-mobile-icon icon-chehui revoke-icon" />
            撤单
          </van-button>
          <van-button @click="onFollowClick">
            <i v-if="!ticketDetail.hasAttention" class="itsm-mobile-icon icon-favorite-o" />
            {{ ticketDetail.hasAttention ? '已关注' : '关注' }}
          </van-button>
        </div>
      </div>
    </div>
    <van-dialog
      v-model:show="isRevokeDialogShow"
      class-name="common-dialog"
      confirm-button-color="#3a84ff"
      cancel-button-color="#3a84ff"
      :show-cancel-button="true"
      :before-close="revokeTicket">
      <div class="van-dialog__message">确定撤销当前单据？</div>
    </van-dialog>
    <van-dialog
      v-model:show="isFollowDialogShow"
      class-name="common-dialog"
      confirm-button-color="#3a84ff"
      cancel-button-color="#3a84ff"
      confirm-button-text="取消关注"
      cancel-button-text="再想想"
      :show-cancel-button="true"
      :before-close="changeFollowStatus">
      <div class="van-dialog__message">取消关注后，将不再接收工单的进度更新</div>
    </van-dialog>
  </div>
</template>
<script lang="ts">
import { defineComponent, toRefs, ref, Ref } from 'vue'
import { useStore } from 'vuex'
import { Toast } from 'vant'

interface Field {
  id: number,
  key: string,
  // eslint-disable-next-line
  display_value: string
}

export default defineComponent({
  name: 'TicketBasicInfo',
  props: {
    ticketDetail: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['revoke'],
  setup(props, { emit }) {
    const { ticketDetail } = toRefs(props)
    const store = useStore()
    const fieldList: Ref<Field[]> = ref([])
    const isRevokeDialogShow = ref(false)
    const isFollowDialogShow = ref(false)

    // 获取影响范围紧急程度
    fieldList.value = ticketDetail.value.table_fields
    fieldList.value.forEach((field: Field) => {
      if (field.key === 'impact') {
        ticketDetail.value.impact = field.display_value
      } else if (field.key === 'urgency') {
        ticketDetail.value.urgency = field.display_value
      }
    })
    // 是否关注单据
    const isAttention = ticketDetail.value.followers.some((name: string) => name === window.username)
    ticketDetail.value.hasAttention = isAttention || false

    const getStatusColor = (ticket) => {
      let color = '#63656e'
      const serviceConfig = store.state.serviceConfig[ticket.service_type]
      if (serviceConfig) {
        color = serviceConfig.find(item => item.key === ticket.current_status).color_hex
      }
      return {
        color,
        borderColor: color
      }
    }

    // 撤单
    const revokeTicket = async (action) => {
      if (action === 'cancel') {
        isRevokeDialogShow.value = false
        return
      }
      try {
        await store.dispatch('ticket/withdraw', { id: ticketDetail.value.id })
        ticketDetail.value.can_withdraw = false
        emit('revoke')
      } catch (error) {
        console.error(error)
      } finally {
        isRevokeDialogShow.value = false
      }
    }

    const onRevokeClick = () => {
      isRevokeDialogShow.value = true
    }

    // 关注/取关
    const changeFollowStatus = async (action) => {
      if (action === 'cancel') {
        isFollowDialogShow.value = false
        return
      }

      const isFollow = !ticketDetail.value.hasAttention
      const params = {
        id: ticketDetail.value.id,
        attention: isFollow
      }
      try {
        await store.dispatch('ticket/addFollower', params)
        ticketDetail.value.hasAttention = isFollow
        Toast.success({
          message: isFollow ? '添加关注成功' : '取消关注成功',
          icon: 'passed',
          className: 'common-toast'
        })
      } catch (error) {
        console.error(error)
      } finally {
        isFollowDialogShow.value = false
      }
    }

    const onFollowClick = () => {
      if (!ticketDetail.value.hasAttention) {
        changeFollowStatus()
      } else {
        isFollowDialogShow.value = true
      }
    }

    return {
      isRevokeDialogShow,
      isFollowDialogShow,
      getStatusColor,
      onRevokeClick,
      revokeTicket,
      onFollowClick,
      changeFollowStatus
    }
  }
})
</script>
<style lang="postcss" scoped>
  .info-content {
    background: #ffffff;
    padding: 24px 32px 16px;
    margin-bottom: 20px;
    color: #8c8c8c;
    &:after {
      border-color: #e6e6e6;
    }
    h5 {
      font-size: 32px;
      color: #222222;
      font-weight: normal;
      line-height: 52px;
      margin-bottom: 16px;
      overflow:hidden;
      text-overflow:ellipsis;
      display:-webkit-box;
      -webkit-line-clamp:2;
      -webkit-box-orient:vertical;
    }
    .info-sn {
      margin-bottom: 11px;
      font-size: 24px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      .ticket-status {
        display: inline-block;
        margin-right: 8px;
        min-width: 64px;
        height: 30px;
        line-height: 30px;
        font-size: 18px;
        text-align: center;
        border: 1px solid #8c8c8c;
        border-radius: 4px;
      }
    }
    & > p {
      margin-bottom: 4px;
      height: 44px;
      line-height: 44px;
      font-size: 24px;
    }
    .info-effect {
      text-align: right;
      .effect-btn {
        .van-button {
          margin-left: 16px;
          padding: 0 16px;
          height: 48px;
          font-size: 26px;
          color: #63656e;
          border-color: #c4c6cc;
          border-radius: 6px;
          i {
            color: #3a84ff;
            font-size: 32px;
          }
        }
      }
    }
  }
</style>
