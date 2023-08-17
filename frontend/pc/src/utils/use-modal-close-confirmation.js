import i18n from '@/i18n/index.js';

export default function useModalCloseConfirmation(title, subTitle) {
  return new Promise(resolve => {
    window.app.$bkInfo({
      title: title || i18n.$t('m["确定离开当前页？"]'),
      subTitle: subTitle || i18n.$t('m["离开将会导致未保存信息丢失"]'),
      okText: i18n.$t('m["离开"]'),
      confirmFn: () => resolve(true),
      cancelFn: () => resolve(false),
    });
  });
}
