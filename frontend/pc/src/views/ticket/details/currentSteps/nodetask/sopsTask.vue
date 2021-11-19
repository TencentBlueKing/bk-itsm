<template>
    <div>
        <sops-get-param
            ref="sopsGetParam"
            :hooked-var-list="hookedVarList"
            :constants="constants"
            :context="context"
            :is-static="isStatic">
        </sops-get-param>
        <bk-button>重做</bk-button>
    </div>
</template>

<script>

    import sopsGetParam from '../../../../processManagement/processDesign/nodeConfigue/components/sopsGetParam.vue'
    export default {
        name: 'sopsTask',
        components: {
            sopsGetParam
        },
        props: {
            nodeInfo: Object,
            constants: Array,
            hookedVarList: Object
        },
        data () {
            return {
                isStatic: false,
                context: {
                    project: {
                        id: '',
                        bk_biz_id: '',
                        name: '',
                        from_cmdb: true
                    },
                    bk_biz_id: '',
                    site_url: window.SITE_URL_SOPS + window.PREFIX_SOPS
                }
            }
        },
        mounted () {
        },
        methods: {
        }
    }
</script>

<style>

</style>
