import { isReadOnly } from '@/utils/readOnly';

export default {
  computed: {
    isReadOnly() {
      return isReadOnly();
    },
  },
};
