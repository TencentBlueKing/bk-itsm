export default function useModalCloseConfirmation(title, subTitle) {
  return new Promise(resolve => {
    window.app.$bkInfo({
      title: title || '确认离开当前页？',
      subTitle: subTitle || '离开会导致未保存信息丢失',
      okText: '离开',
      confirmFn: () => resolve(true),
      cancelFn: () => resolve(false),
    });
  });
}
