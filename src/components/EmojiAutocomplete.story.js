import { storybookDefaults as defaults } from '>/helpers'
import { storiesOf } from '@storybook/vue'

import EmojiAutocomplete from './EmojiAutocomplete'

storiesOf('EmojiAutocomplete', module)
  .add('Default', () => defaults({
    render: h => h(EmojiAutocomplete),
  }))
