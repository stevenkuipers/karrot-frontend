<template>
  <div>
    <q-input
      v-model="term"
    />
    <q-list dense>
      <q-item
        v-for="[name, code] in filtered"
        :key="name"
        @click="$emit(name)"
        class="row items-start"
      >
        <span
          class="emojipreview"
          v-html="picture(code)"
        />
        <span style="margin-left: 8px">:{{ name }}:</span>
      </q-item>
    </q-list>
  </div>
</template>

<script>
import {
  QList,
  QItem,
  QInput,
} from 'quasar'
import emojiList from 'markdown-it-emoji/lib/data/light.json'
import twemoji from 'twemoji'

export default {
  components: {
    QList,
    QItem,
    QInput,
  },
  data () {
    return {
      term: '',
    }
  },
  methods: {
    picture (code) {
      return twemoji.parse(code)
    },
  },
  computed: {
    filtered () {
      return Object.entries(emojiList).filter(([name, code]) => name.includes(this.term.replace(':', '').toLowerCase()))
    },
  },
}
</script>

<style scoped lang="stylus">
.emojipreview >>> img.emoji
  height 1.1em
  width 1.1em
  margin 0 .05em 0 .1em
  vertical-align -0.1em
</style>
