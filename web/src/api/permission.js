import request from "@/utils/request";

export function getPermissionList() {
  return request({
    url: "/accounts/permissions/",
    method: "get",
  });
}

export function createPermission(data) {
  return request({
    url: "/accounts/permissions/",
    data: data,
    method: "post",
  });
}

export function updatePermission(data) {
  return request({
    url: `/accounts/permissions/${data.id}/`,
    data: data,
    method: "put",
  });
}

export function deletePermission(id) {
  return request({
    url: `/accounts/permissions/${id}/`,
    method: "delete",
  });
}
