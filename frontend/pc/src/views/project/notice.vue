<template>
    <div class="bk-itsm-service">
        <div class="is-title" :class="{ 'bk-title-left': !sliderStatus }">
            <p class="bk-come-back">
                {{ $t('m["通知配置"]') }}
            </p>
        </div>
    </div>
</template>

<script>

    export default {
        name: 'Notice',
        computed: {
            sliderStatus () {
                return this.$store.state.common.slideStatus
            }
        }
    }

</script>

<style>

</style>
