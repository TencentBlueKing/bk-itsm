<template>
    <div class="wang-editor">
        <div :id="editorId">
        </div>
        <!-- <ul class="bullet-box" :style="{ left: left + 'px', top: top + 'px', display: showFlag }">
            <li v-for="item in list" :key="item.key" @click="selectLine(item)">
                {{item.name}}
            </li>
        </ul> -->
    </div>
</template>

<script>
    import E from 'wangeditor'
    import { position, offset } from 'caret-pos'
    export default {
        name: 'wangEditor',
        props: {
            editorId: String
        },
        data () {
            return {
                editor: null,
                editorData: '',
                left: '0px',
                top: '0px',
                showFlag: 'none',
                list: [
                    {
                        name: 'admin',
                        key: '1'
                    },
                    {
                        name: 'zyx',
                        key: '2'
                    },
                    {
                        name: 'mark',
                        key: '3'
                    }
                ]
            }
        },
        watch: {
            editorData () {
                const text = this.editor.txt.text()
                this.$emit('changebuttonStatus', !!text)
                if (text.charAt(text.length - 1) === '@') {
                    this.showFlag = 'block'
                    const textDom = this.editor.$textElem.elems[0]
                    const pos = position(textDom) // { left: 15, top: 30, height: 20, pos: 15 }
                    const off = offset(textDom)
                    console.log(pos, off)
                    const wangED = document.querySelector(`#${this.editorId}`)
                    // 菜单的高度
                    const menuH = wangED.offsetHeight - textDom.offsetHeight
                    this.left = pos.left
                    this.top = menuH + pos.height + pos.top
                    // const childEle = document.getElementsByClassName('bullet-box')[0]
                    // console.log(childEle)
                } else {
                    this.showFlag = 'none'
                }
            }
        },
        mounted () {
            const editor = new E(`#${this.editorId}`)
            editor.config.onchange = (newHtml) => {
                this.editorData = newHtml
                this.$emit('editorContent', newHtml)
            }
            editor.config.height = 150
            editor.config.zIndex = 400
            editor.create()
            this.editor = editor
        },
        methods: {
            selectLine (item) {
                const text = this.editor.txt.text()
                console.log(text)
                this.editor.txt.html(text + `<span class="at-person">${item.name}<span>` + '  ')
            }
        }
    }
</script>

<style lang="scss" scoped>
.at-person {
    color: #3A84FF;
}
.wang-editor {
    position: relative;
    .bullet-box {
        width: 100px;
        min-height: 50px;
        background-color: darkgray;
        z-index: 501;
        position: absolute;
    }
}
</style>
