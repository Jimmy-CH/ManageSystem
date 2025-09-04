import request from "@/utils/request";

export function getList(params) {
  return request({
    url: "/vue-admin-template/table/list",
    method: "get",
    params,
  });
}

export function getUserList() {
  return request({
    url: "/accounts/user-profile/",
    method: "get",
  });
}

export function getRoleList() {
  return request({
    url: "/accounts/roles/",
    method: "get",
  });
}
