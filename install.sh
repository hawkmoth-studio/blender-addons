#!/usr/bin/env bash

BLENDER_VERSION="2.83"
BLENDER_ADDONS_DIR="/Users/$(id -u -n)/Library/Application Support/Blender/${BLENDER_VERSION}/scripts/addons"


function module_install() {
  local addon_name="${1}"
  local addon_dir="${BLENDER_ADDONS_DIR}/${addon_name}"

  echo "Uninstalling '${addon_dir}'..."
  __result=$(
    (
      rm -rf "${addon_dir}"
    ) 2>&1
  ) || (
    echo "Uninstalling '${addon_dir}' from '${addon_dir}': failed!"
    echo "${__result}"
    return 1
  ) || return 1

  echo "Installing '${addon_name}'..."
  __result=$(
    (
      mkdir -pv "${addon_dir}" &&
      cp -rvf "./${addon_name}"/* "${addon_dir}/"
    ) 2>&1
  ) || (
    echo "Installing '${addon_name}' to '${addon_dir}': failed!"
    echo "${__result}"
    return 1
  ) || return 1

  echo "Module '${addon_name}' successfully installed to '${addon_dir}'."
  return 0
}


module_install "hawkmoth_rigging_tools"
