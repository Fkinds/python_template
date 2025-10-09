#!/bin/bash
set -e

# このスクリプトは、UID/GIDを1001に固定し、コンテナ内ユーザーのUID/GIDを変更し、
# そのユーザー権限でアプリを起動します。

USER=$(whoami)
HOME=/home/$USER

# 固定UID/GID
uid=1001
gid=1001

# UID/GIDがrootでも既存UIDでもない場合のみ変更
if [ "$uid" -ne 0 ] && [ "$uid" -ne "$(id -u $USER)" ]; then
    usermod -u $uid $USER
    groupmod -g $gid $USER
    chown -R $uid:$gid $HOME
    chown -R $uid:$gid /home/$USER/app
fi

# 非rootユーザーでアプリ起動
exec setpriv --reuid=$uid --regid=$gid --init-groups python -m app
