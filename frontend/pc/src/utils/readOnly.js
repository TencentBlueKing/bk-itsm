export function isReadOnly() {
  return !!window.ITSM_READ_ONLY_MODE;
}

export function guardWriteAction(vm, action = '该操作') {
  if (!isReadOnly()) return false;
  if (vm.$bkMessage) {
    vm.$bkMessage({
      theme: 'warning',
      message: `当前为只读模式，${action}已被禁用`,
      delay: 3000,
      limit: 1,
    });
  }
  return true;
}
