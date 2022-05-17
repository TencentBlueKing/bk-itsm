/*
 * Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
 *
 * License for BK-ITSM 蓝鲸流程服务:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

export class ProcessTools {
  constructor(allNode, allLine) {
    this.allNode = allNode;
    this.allLine = allLine;
    this.startNodeId = allNode.find(node => node.type === 'START').id;
    this.endNodeId = allNode.find(node => node.type === 'END').id;
    this.getAllPath();
  }
  // 获取所有路径
  getAllPath() {
    const self = this;
    const allPath = [];
    const start = self.startNodeId;
    const end = self.endNodeId;
    function getPath(begin, last, path = null) {
      if (!path) {
        path = [];
      }
      if (begin === last) {
        allPath.push(path.slice(0));
      }
      for (let i = 0; i < self.allLine.length; i++) {
        const line = self.allLine[i];
        if (line.from_state === begin) {
          if (path.includes(line.to_state)) {
            continue;
          }
          path.push(line.to_state);
          getPath(line.to_state, last, path);
          path.pop();
        }
      }
    }
    getPath(start, end);
    self.allPath = allPath;
    return allPath;
  }
  // 获取某个节点后面的可选节点
  getAfterNodes(nodeId) {
    const nodes = [];
    this.allPath.forEach((path) => {
      const index = path.indexOf(nodeId);
      if (index !== -1) {
        const pathAfter = path.slice(index + 1);
        pathAfter.forEach((n) => {
          if (!nodes.includes(n)) nodes.push(n);
        });
      }
    });
    return this.allNode.filter(node => nodes.includes(node.id)
            && node.name !== '' && node.type !== 'START' && node.type !== 'END');
  }
  /**
     * 获取某个节点 sla 可选结束节点
     * @param {Number} startNode 开始节点 id
     * @description
     * 从后置节点中过滤出包含 S E 的所有路径，且每一条路径中都含有 S E 节点
     */
  getSlaAfterNodes(startNode) {
    const self = this;
    const afterNodes = self.getAfterNodes(startNode);
    return afterNodes.filter((node) => {
      // 包含开始节点或结束节点的所有路径
      const throughPath = self.allPath.filter(path => path.includes(startNode) || path.includes(node.id));
      return throughPath.every(n => n.includes(startNode) && n.includes(node.id));
    });
  }
}
