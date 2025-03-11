//  algorithm
// The Virtual DOM is a lightweight JavaScript representation of
// the actual DOM (Document Object Model). It's essentially a copy of the real
// DOM tree kept in memory.

// steps
// Creation: When your application renders, the framework creates a virtual representation of the DOM in memory.
// Updating: When data changes in your application:

// A new virtual DOM tree is created
// This new tree is compared with the previous virtual DOM tree
// The differences (or "diff") between the two trees are calculated

// Reconciliation: Only the elements that have changed are updated in the real DOM.

const createTextElement = (text) => {
  return {
    type: "TEXT_ELEMENT",
    props: {},
    children: [],
    value: text,
  };
};

// The createElement function is a helper function that creates a virtual node.
// 1. Creating repreasentation of a virtual DOM node
const createElement = (type, props = {}, ...children) => {
  return {
    type,
    props,
    children: children
      .flat()
      .map((child) =>
        typeof child === "object" ? child : createTextElement(child)
      ),
  };
};

// 2. Create a real DOM node from virtual DOM
const createRealDOMNode = (vNode) => {
  // Handle text nodes
  if (vNode.type === "TEXT_ELEMENT") {
    return document.createTextNode(vNode.value);
  }

  // Create the DOM element idf not a text node and where
  // vNode.type is the type of the element (e.g., "div", "span").

  const domNode = document.createElement(vNode.type);

  // Add attributes/props
  Object.keys(vNode.props).forEach((propName) => {
    //  If a property name starts with "on", it is treated as an event listener
    // (e.g., "onClick"). The event name is extracted by removing the "on" prefix
    //  and converting the rest to lowercase, and the event listener is added.
    if (propName.startsWith("on")) {
      // Handle event listeners -
      const eventName = propName.substring(2).toLowerCase();
      domNode.addEventListener(eventName, vNode.props[propName]);
    } else {
      // Handle regular attributes
      domNode.setAttribute(propName, vNode.props[propName]);
    }
  });

  // Create and append children
  // The function iterates over the children of the virtual node (vNode.children).
  // For each child virtual node, it recursively calls
  // createRealDOMNode(childVNode) to create the corresponding real DOM node
  // and appends it to the parent DOM node using domNode.appendChild(childDomNode).
  vNode.children.forEach((childVNode) => {
    const childDomNode = createRealDOMNode(childVNode);
    domNode.appendChild(childDomNode);
  });

  return domNode;
};

// 3. Compare and update - the diff algorithm
// The updateElement function compares the new virtual node (newVNode) with the old virtual node (oldVNode).
// If the two nodes are different, the function updates the real DOM node to match the new virtual node.
// If the nodes are the same, the function recursively updates the children of the nodes.
// The function takes the parent DOM node, the new virtual node, the old virtual node, and an optional index parameter
// (used to track the position of the node in the parent's child nodes) as arguments.
// This process is often referred to as "reconciliation" or "diffing."
const updateElement = (parent, newVNode, oldVNode, index = 0) => {
  // If old node doesn't exist it means this is a new node that needs to be added
  //  to the real DOM. The function creates a real DOM node from the
  // new virtual DOM node (newVNode) and appends it to the parent. Simply append new node
  if (!oldVNode) {
    parent.appendChild(createRealDOMNode(newVNode));
    return;
  }

  // If new node doesn't exist, remove the old node
  if (!newVNode) {
    parent.removeChild(parent.childNodes[index]);
    return;
  }

  // If node types are different, replace old with new
  if (newVNode.type !== oldVNode.type) {
    parent.replaceChild(createRealDOMNode(newVNode), parent.childNodes[index]);
    return;
  }

  // If node types are the same, update props
  if (newVNode.type !== "TEXT_ELEMENT") {
    const newProps = newVNode.props || {};
    const oldProps = oldVNode.props || {};

    // Add or update props. he function iterates over the new props and
    // updates the real DOM node if the prop value has changed.
    Object.keys(newProps).forEach((propName) => {
      if (newProps[propName] !== oldProps[propName]) {
        if (propName.startsWith("on")) {
          const eventName = propName.substring(2).toLowerCase();
          parent.childNodes[index].removeEventListener(
            eventName,
            oldProps[propName]
          );
          parent.childNodes[index].addEventListener(
            eventName,
            newProps[propName]
          );
        } else {
          parent.childNodes[index].setAttribute(propName, newProps[propName]);
        }
      }
    });

    // Remove props that don't exist in new node.
    //  The function iterates over the old props and removes them from the
    // real DOM node if they don't exist in the new props.
    Object.keys(oldProps).forEach((propName) => {
      if (!newProps[propName]) {
        if (propName.startsWith("on")) {
          const eventName = propName.substring(2).toLowerCase();
          parent.childNodes[index].removeEventListener(
            eventName,
            oldProps[propName]
          );
        } else {
          parent.childNodes[index].removeAttribute(propName);
        }
      }
    });

    // Recursively update children
    const maxLength = Math.max(
      newVNode.children.length,
      oldVNode.children.length
    );
    for (let i = 0; i < maxLength; i++) {
      updateElement(
        parent.childNodes[index],
        newVNode.children[i],
        oldVNode.children[i],
        i
      );
    }
  } else if (newVNode.value !== oldVNode.value) {
    // Update text node If the virtual DOM nodes are text nodes and their values are different,
    // the function updates the text content of the real DOM node.
    parent.childNodes[index].nodeValue = newVNode.value;
  }
};

// 4. Simple component system with state
class Component {
  constructor(props = {}) {
    this.props = props;
    this.state = {};
    this._vNode = null;
    this._domNode = null;
    this._mounted = false;
  }

  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.update();
  }

  update() {
    if (!this._mounted) return;

    const newVNode = this.render();
    updateElement(
      this._domNode.parentNode,
      newVNode,
      this._vNode,
      Array.from(this._domNode.parentNode.childNodes).indexOf(this._domNode)
    );
    this._vNode = newVNode;
  }

  mount(domNode) {
    this._vNode = this.render();
    this._domNode = createRealDOMNode(this._vNode);
    domNode.appendChild(this._domNode);
    this._mounted = true;
  }

  render() {
    throw new Error("Component must implement render method");
  }
}

const demo = () => {
  // Initial state of our UI
  // should look something like this -
  // <div class="container">
  //   <h1>Virtual DOM Demo</h1>
  //   <p>This is a demonstration of how Virtual DOM works.</p>
  //   <ul>
  //     <li class="item">Item 1</li>
  //     <li class="item">Item 2</li>
  //   </ul>
  // </div>
  const initialVDOM = createElement(
    "div",
    { class: "container" },
    createElement("h1", {}, "Virtual DOM Demo"),
    createElement("p", {}, "This is a demonstration of how Virtual DOM works."),
    createElement(
      "ul",
      {},
      createElement("li", { class: "item" }, "Item 1"),
      createElement("li", { class: "item" }, "Item 2")
    )
  );

  // Create real DOM from virtual DOM
  const rootElement = document.getElementById("root");
  rootElement.appendChild(createRealDOMNode(initialVDOM));

  // After 2 seconds, update the DOM with new Virtual DOM
  // SHould look like this -
  // <div class="container active">
  //   <h1>Virtual DOM Demo</h1>
  //   <p>This is an updated demonstration.</p>
  //   <ul>
  //     <li class="item">Item 1</li>
  //     <li class="item highlighted">Updated Item 2</li>
  //     <li class="item">Item 3</li>
  //   </ul>
  // </div>
  setTimeout(() => {
    console.log("Updating DOM...");

    // Updated state of our UI with some changes
    const updatedVDOM = createElement(
      "div",
      { class: "container active" }, // Changed class
      createElement("h1", {}, "Virtual DOM Demo"),
      createElement("p", {}, "This is an updated demonstration."), // Changed text
      createElement(
        "ul",
        {},
        createElement("li", { class: "item" }, "Item 1"),
        createElement("li", { class: "item highlighted" }, "Updated Item 2"), // Changed class and text
        createElement("li", { class: "item" }, "Item 3") // New item
      )
    );

    // Update using our diffing algorithm
    updateElement(rootElement, updatedVDOM, initialVDOM);

    // Log what was updated in the real DOM
    console.log("DOM updated!");
  }, 2000);
};

// Run the demo when the page loads
window.onload = demo;
