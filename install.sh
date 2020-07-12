#!/usr/bin/env bash

BLENDER_VERSION="2.83"
BLENDER_ADDONS_DIR="/Users/$(id -u -n)/Library/Application Support/Blender/${BLENDER_VERSION}/scripts/addons"


function addon_install() {
  local addon_name="${1}"
  local addon_source_dir="./${addon_name}"
  local addon_target_dir="${BLENDER_ADDONS_DIR}/${addon_name}"

  echo "Uninstalling '${addon_name}'..."
  __result=$(
    (
      rm -rf "${addon_target_dir}"
    ) 2>&1
  ) || (
    echo "Uninstalling '${addon_target_dir}' from '${addon_target_dir}': failed!"
    echo "${__result}"
    return 1
  ) || return 1

  echo "Installing '${addon_name}'..."
  __result=$(
    (
      mkdir -pv "${addon_target_dir}" &&
      cp -rvf "${addon_source_dir}"/* "${addon_target_dir}/"
    ) 2>&1
  ) || (
    echo "Installing '${addon_name}' to '${addon_target_dir}': failed!"
    echo "${__result}"
    return 1
  ) || return 1

  echo "Addon '${addon_name}' successfully installed to '${addon_target_dir}'."
  return 0
}


addon_install "hawkmoth_rigging_tools"
