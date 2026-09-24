/** Fixture for the odoo-workflow W2 grep. FLAG lines must match; the rest stays silent. */
import { patch } from "@web/core/utils/patch";

export class XRenderer extends Component {} // FLAG:js-class
export class XRendererExtra extends Component {}
patch(XRenderer.prototype, { setup() {} }); // FLAG:js-class
patch(XRendererExtra.prototype, {});
const other = new XRenderer();
