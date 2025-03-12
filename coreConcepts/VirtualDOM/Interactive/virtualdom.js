class VirtualDOM {
  // Helper for text nodes
  createTextElement = (text) => {
    return {
      type: "TEXT_ELEMENT",
      props: {},
      children: [],
      value: String(text),
      id: Math.random().toString(36).substr(2, 9),
    };
  };

  // Create virtual DOM element
  createElement(type, props = {}, ...children) {
    const flatChildren = children
      .flat()
      .filter((child) => child !== null && child !== undefined);
    return {
      type,
      props,
      children: flatChildren.map((child) =>
        typeof child === "object" ? child : this.createTextElement(child)
      ),
      id: Math.random().toString(36).substr(2, 9), // unique ID for tracking
    };
  }

  // Create real DOM from virtual node
  createRealDOMNode(vNode) {
    const log = (msg) => this.logOperation("create", msg);

    // Handle text nodes
    if (vNode.type === "TEXT_ELEMENT") {
      log(`Created text node: "${vNode.value}"`);
      const node = document.createTextNode(vNode.value);
      // Text nodes do not support dataset, so we skip setting the id
      return node;
    }

    // Create element
    log(`Created ${vNode.type} element`);
    const domNode = document.createElement(vNode.type);
    domNode.dataset.id = vNode.id;

    // Set attributes
    Object.keys(vNode.props).forEach((propName) => {
      if (propName === "className") {
        domNode.setAttribute("class", vNode.props[propName]);
        log(`Set class="${vNode.props[propName]}"`);
      } else if (propName !== "children") {
        domNode.setAttribute(propName, vNode.props[propName]);
        log(`Set ${propName}="${vNode.props[propName]}"`);
      }
    });

    // Create and append children
    vNode.children.forEach((childVNode) => {
      const childDomNode = this.createRealDOMNode(childVNode);
      domNode.appendChild(childDomNode);
    });

    return domNode;
  }

  // Find differences and update real DOM
  updateElement(parent, newVNode, oldVNode, index = 0) {
    // If old node doesn't exist, add new node
    if (!oldVNode) {
      const newNode = this.createRealDOMNode(newVNode);
      parent.appendChild(newNode);
      this.logOperation("add", `Added new ${newVNode.type} element`);
      this.highlightElement(newNode);
      return;
    }

    // If new node doesn't exist, remove the old node
    if (!newVNode) {
      const nodeToRemove = parent.childNodes[index];
      this.logOperation(
        "remove",
        `Removed ${nodeToRemove.nodeName.toLowerCase()} element`
      );
      this.highlightElement(nodeToRemove, "remove");
      setTimeout(() => {
        parent.removeChild(nodeToRemove);
      }, 500);
      return;
    }

    // If node types are different, replace old with new
    if (newVNode.type !== oldVNode.type) {
      const oldNode = parent.childNodes[index];
      const newNode = this.createRealDOMNode(newVNode);
      this.logOperation(
        "update",
        `Replaced ${oldVNode.type} with ${newVNode.type}`
      );
      this.highlightElement(oldNode, "update");
      setTimeout(() => {
        parent.replaceChild(newNode, oldNode);
        this.highlightElement(newNode);
      }, 500);
      return;
    }

    // If node is a text element and text changed
    if (newVNode.type === "TEXT_ELEMENT" && oldVNode.type === "TEXT_ELEMENT") {
      if (newVNode.value !== oldVNode.value) {
        const textNode = parent.childNodes[index];
        this.logOperation(
          "update",
          `Updated text from "${oldVNode.value}" to "${newVNode.value}"`
        );
        this.highlightElement(textNode, "update");
        setTimeout(() => {
          textNode.nodeValue = newVNode.value;
        }, 500);
      }
      return;
    }

    // Update attributes
    if (newVNode.type !== "TEXT_ELEMENT") {
      const element = parent.childNodes[index];
      const newProps = newVNode.props || {};
      const oldProps = oldVNode.props || {};

      // Remove old props
      Object.keys(oldProps).forEach((propName) => {
        if (propName !== "children" && !newProps[propName]) {
          if (propName === "className") {
            element.removeAttribute("class");
            this.logOperation("update", `Removed class attribute`);
          } else {
            element.removeAttribute(propName);
            this.logOperation("update", `Removed ${propName} attribute`);
          }
          this.highlightElement(element, "update");
        }
      });

      // Add or update props
      Object.keys(newProps).forEach((propName) => {
        if (
          propName !== "children" &&
          newProps[propName] !== oldProps[propName]
        ) {
          if (propName === "className") {
            element.setAttribute("class", newProps[propName]);
            this.logOperation(
              "update",
              `Updated class from "${oldProps[propName] || ""}" to "${
                newProps[propName]
              }"`
            );
          } else {
            element.setAttribute(propName, newProps[propName]);
            this.logOperation(
              "update",
              `Updated ${propName} from "${oldProps[propName] || ""}" to "${
                newProps[propName]
              }"`
            );
          }
          this.highlightElement(element, "update");
        }
      });
    }

    // Recursively update children
    const oldChildren = oldVNode.children || [];
    const newChildren = newVNode.children || [];
    const maxLength = Math.max(oldChildren.length, newChildren.length);

    for (let i = 0; i < maxLength; i++) {
      this.updateElement(
        parent.childNodes[index],
        newChildren[i],
        oldChildren[i],
        i
      );
    }
  }

  // Highlight elements for visual feedback
  highlightElement(element, type = "add") {
    if (!element || !element.classList) return;

    element.classList.add("highlight");
    if (type === "update") {
      element.classList.add("diff-highlight");
    }

    setTimeout(() => {
      element.classList.remove("highlight");
      element.classList.remove("diff-highlight");
    }, 2000);
  }

  // Log operations for visualization
  logOperation(type, message) {
    const logsElement = document.getElementById("logs");
    const logItem = document.createElement("div");
    logItem.className = `operation ${type}`;
    logItem.textContent = `${type.toUpperCase()}: ${message}`;
    logsElement.prepend(logItem);

    // Limit log items
    if (logsElement.children.length > 20) {
      logsElement.removeChild(logsElement.lastChild);
    }
  }

  // Pretty print vdom for display
  printVDOM(vNode, indent = 0) {
    if (!vNode) return "";

    const spacing = " ".repeat(indent * 2);

    if (vNode.type === "TEXT_ELEMENT") {
      return `${spacing}"${vNode.value}"\n`;
    }

    let result = `${spacing}<${vNode.type}`;

    // Add props
    Object.keys(vNode.props).forEach((prop) => {
      if (prop !== "children") {
        if (prop === "className") {
          result += ` class="${vNode.props[prop]}"`;
        } else {
          result += ` ${prop}="${vNode.props[prop]}"`;
        }
      }
    });

    result += ">";

    // Add children
    if (vNode.children && vNode.children.length > 0) {
      result += "\n";
      vNode.children.forEach((child) => {
        result += this.printVDOM(child, indent + 1);
      });
      result += `${spacing}</${vNode.type}>\n`;
    } else {
      result += `</${vNode.type}>\n`;
    }

    return result;
  }
}

// Application state
class App {
  constructor() {
    this.vdom = new VirtualDOM();
    this.rootVDOM = this.vdom.createElement("div", { id: "app-root" });
    this.prevVDOM = null;
    this.elementsMap = new Map();

    this.init();
  }

  init() {
    // Initialize the DOM
    const rootElement = document.getElementById("root");
    const rootNode = this.vdom.createRealDOMNode(this.rootVDOM);
    rootElement.appendChild(rootNode);

    // Update VDOM display
    this.updateVDOMDisplay();

    // Set up event listeners
    this.setupEventListeners();

    // Update both select elements
    this.updateSelectElements();

    // Generate the initial graph
    this.generateGraph();
  }

  setupEventListeners() {
    // Add element button
    document.getElementById("add-element").addEventListener("click", () => {
      this.addElement();
    });

    // Update element button
    document.getElementById("update-element").addEventListener("click", () => {
      this.updateElement();
    });

    // Remove element button
    document.getElementById("remove-element").addEventListener("click", () => {
      this.removeElement();
    });
  }

  addElement() {
    const type = document.getElementById("element-type").value;
    const text = document.getElementById("element-text").value;
    const className = document.getElementById("element-class").value;
    const parentId = document.getElementById("parent-element").value;

    // Create props object
    const props = {};
    if (className) props.className = className;

    // Create new element
    const newElement = this.vdom.createElement(type, props, text);

    // Store for selection
    const id = newElement.id;
    this.elementsMap.set(id, newElement);

    // Find the parent node in our virtual DOM
    const findAndAddChild = (vNode) => {
      if (vNode.id === parentId) {
        vNode.children.push(newElement);
        return true;
      }

      // Recurse through children
      if (vNode.children) {
        for (let child of vNode.children) {
          if (findAndAddChild(child)) return true;
        }
      }

      return false;
    };

    // Save the previous state
    this.prevVDOM = JSON.parse(JSON.stringify(this.rootVDOM));

    // Add to the selected parent or root if no parent selected
    if (parentId) {
      findAndAddChild(this.rootVDOM);
    } else {
      this.rootVDOM.children.push(newElement);
    }

    // Update real DOM
    const rootElement = document.getElementById("root");
    this.vdom.updateElement(rootElement, this.rootVDOM, this.prevVDOM);

    // Update displays
    this.updateVDOMDisplay();
    this.updateSelectElements();

    // Update the graph
    this.generateGraph();
  }

  updateElement() {
    const selectId = document.getElementById("select-element").value;
    if (!selectId) return;

    const newText = document.getElementById("update-text").value;
    const newClass = document.getElementById("update-class").value;

    // Find and update the element
    const updateNode = (vNode) => {
      if (vNode.id === selectId) {
        // Save the previous state
        this.prevVDOM = JSON.parse(JSON.stringify(this.rootVDOM));

        if (vNode.type === "TEXT_ELEMENT") {
          vNode.value = newText || vNode.value;
        } else {
          // Update text node
          if (
            vNode.children.length > 0 &&
            vNode.children[0].type === "TEXT_ELEMENT"
          ) {
            vNode.children[0].value = newText || vNode.children[0].value;
          } else if (newText) {
            // Add a new text node
            vNode.children.unshift(this.vdom.createTextElement(newText));
          }

          // Update class
          if (newClass !== "") {
            vNode.props.className = newClass;
          }
        }
        return true;
      }

      // Recurse through children
      if (vNode.children) {
        for (let child of vNode.children) {
          if (updateNode(child)) return true;
        }
      }

      return false;
    };

    updateNode(this.rootVDOM);

    // Update real DOM
    const rootElement = document.getElementById("root");
    this.vdom.updateElement(rootElement, this.rootVDOM, this.prevVDOM);

    // Update displays
    this.updateVDOMDisplay();
    this.updateSelectElements();

    // Update the graph
    this.generateGraph();
  }

  removeElement() {
    const selectId = document.getElementById("select-element").value;
    if (!selectId) return;

    // Find and remove the element
    const removeNode = (vNode, parentArray) => {
      if (vNode.id === selectId) {
        const index = parentArray.indexOf(vNode);
        if (index !== -1) {
          parentArray.splice(index, 1);
          return true;
        }
      }

      // Recurse through children
      if (vNode.children) {
        for (let i = 0; i < vNode.children.length; i++) {
          if (removeNode(vNode.children[i], vNode.children)) return true;
        }
      }

      return false;
    };

    // Save the previous state
    this.prevVDOM = JSON.parse(JSON.stringify(this.rootVDOM));

    // Try to remove from root's children
    if (!removeNode(this.rootVDOM, [this.rootVDOM])) {
      // If not found directly, search through children
      this.rootVDOM.children.forEach((child) => {
        removeNode(child, this.rootVDOM.children);
      });
    }

    // Update real DOM
    const rootElement = document.getElementById("root");
    this.vdom.updateElement(rootElement, this.rootVDOM, this.prevVDOM);

    // Remove from element map
    this.elementsMap.delete(selectId);

    // Update displays
    this.updateVDOMDisplay();
    this.updateSelectElements();

    // Update the graph
    this.generateGraph();
  }

  updateVDOMDisplay() {
    const vdomDisplay = document.getElementById("vdom-display");
    vdomDisplay.textContent = this.vdom.printVDOM(this.rootVDOM);
  }

  // Combined method to update both select elements
  updateSelectElements() {
    const selectElement = document.getElementById("select-element");
    const parentSelect = document.getElementById("parent-element");

    // Clear options except the first
    while (selectElement.options.length > 1) {
      selectElement.remove(1);
    }
    while (parentSelect.options.length > 1) {
      parentSelect.remove(1);
    }

    // Helper to gather elements recursively
    const gatherElements = (vNode, prefix = "") => {
      if (!vNode) return;

      // Skip the root node for select element (we don't want to select the root)
      if (vNode.id !== this.rootVDOM.id) {
        let displayName;

        if (vNode.type === "TEXT_ELEMENT") {
          displayName = `"${vNode.value.substring(0, 20)}${
            vNode.value.length > 20 ? "..." : ""
          }"`;
        } else {
          displayName = `<${vNode.type}>`;
          if (vNode.props.className) {
            displayName += ` .${vNode.props.className}`;
          }
        }

        // Add to select element dropdown (elements that can be selected for update/remove)
        const option = document.createElement("option");
        option.value = vNode.id;
        option.textContent = `${prefix}${displayName}`;
        selectElement.appendChild(option);

        // Only add element nodes as potential parents (not text nodes)
        if (vNode.type !== "TEXT_ELEMENT") {
          const parentOption = document.createElement("option");
          parentOption.value = vNode.id;
          parentOption.textContent = `${prefix}${displayName}`;
          parentSelect.appendChild(parentOption);
        }
      }

      // Recurse through children
      if (vNode.children) {
        const newPrefix = prefix + (vNode.id !== this.rootVDOM.id ? "  " : "");
        vNode.children.forEach((child) => {
          gatherElements(child, newPrefix);
        });
      }
    };

    // Add root element as a potential parent
    const rootOption = document.createElement("option");
    rootOption.value = this.rootVDOM.id;
    rootOption.textContent = `<${this.rootVDOM.type}> #app-root`;
    parentSelect.appendChild(rootOption);

    // Gather all elements
    gatherElements(this.rootVDOM);
  }

  generateGraph() {
    const elements = [];

    const traverseVDOM = (vNode, parentId = null) => {
      const nodeId = vNode.id;
      const label = vNode.type === "TEXT_ELEMENT" ? vNode.value : vNode.type;
      elements.push({
        data: { id: nodeId, label: label },
      });

      if (parentId) {
        elements.push({
          data: { source: parentId, target: nodeId },
        });
      }

      vNode.children.forEach((child) => {
        traverseVDOM(child, nodeId);
      });
    };

    traverseVDOM(this.rootVDOM);

    const cy = cytoscape({
      container: document.getElementById("dom-graph"),
      elements: elements,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "background-color": "#4b5563",
            color: "#ffffff",
            "font-size": "12px",
            "border-width": 2,
            "border-color": "#ffffff",
            width: "label",
            height: "label",
            padding: "10px",
            shape: "round-rectangle",
          },
        },
        {
          selector: "edge",
          style: {
            width: 3,
            "line-color": "#4b5563",
            "target-arrow-color": "#4b5563",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
          },
        },
      ],
      layout: {
        name: "breadthfirst",
        directed: true,
        padding: 10,
        spacingFactor: 1.5,
      },
    });
  }
}

// Initialize the app when the page loads
window.onload = () => {
  new App();
};
