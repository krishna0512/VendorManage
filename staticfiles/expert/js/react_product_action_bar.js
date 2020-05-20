'use strict';

class Icon extends React.Component {
    render() {
        this.cn = "fa fa-" + this.props.name;
        if (this.props.large) {
            this.cn += ' fa-lg';
        }
        return (
            <i className={this.cn}></i>
        );
    }
}

class Spinner extends React.Component {
    render() {
        return (
            <i className="fa fa-spinner fa-pulse fa-fw fa-lg"></i>
        );
    }
}

class Button extends React.Component {
    render() {
        var className = "btn btn-"
        var fnClick = this.props.onClick
        if (this.props.variant) {
            className += this.props.variant;
        }
        else {
            className += "default";
        }
        if (this.props.size) {
            className += " btn-" + this.props.size;
        }
        if (this.props.extraClass) {
            className += " " + this.props.extraClass;
        }
        if (this.props.disabled) {
            className += " disabled";
            return (
                <button className={className}>{this.props.children}</button>
            );
        }
        return (
            <button className={className} onClick={this.props.onClick}>{this.props.children}</button>
        );
    }
}

class CompleteButton extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        if (this.props.isLoading) {
            return (
                <div>
                    <Button variant="outline-success" size="sm" disabled extraClass={this.props.extraClass}>
                        <Spinner />
                    </Button>
                </div>
            );
        }
        if (this.props.product.is_dispatched || this.props.product.is_returned) {
            return (
                <div>
                    <Button variant="outline-success" size="sm" disabled extraClass={this.props.extraClass}>
                        <Icon name="check" large />
                    </Button>
                </div>
            );
        }
        else if (this.props.product.is_completed) {
        // else if (this.state.completed) {
            return (
                <div>
                    <Button variant="outline-warning" onClick={this.props.handleUncomplete} size="sm" extraClass={this.props.extraClass}>
                        <Icon name="ban" large />
                    </Button>
                </div>
            );
        }
        else {
        // product is assigned but not completed
            return (
                <div>
                    <Button variant="outline-success" onClick={this.props.handleComplete} size="sm" extraClass={this.props.extraClass}>
                        <Icon name="check" large />
                    </Button>
                </div>
            );
        }
    }
}

class Dropdown extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        var cn = "btn btn-sm btn-outline-danger dropdown-toggle"
        if (this.props.disabled) cn += " disabled";
        return (
            <div className="dropdown">
                <button
                    className={cn}
                    type="button" id={this.props.id}
                    extraClass={this.props.extraClass}
                    data-toggle="dropdown" aria-haspopup="true"
                    aria-expanded="false" title={this.props.title}
                >
                    {this.props.text}
                </button>
                <div className="dropdown-menu" aria-labelledby={this.props.id}>
                    {this.props.children}
                </div>
            </div>
        );
    }
}

class ReturnButton extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        if (this.props.isLoading) {
            return (
                <Dropdown id="returndropdownreact" text={<Spinner />} title="Returned Products" extraClass={this.props.extraClass} />
            );
        }
        if (this.props.product.is_dispatched && this.props.product.is_returned) {
            return (
                <Dropdown id="returndropdownreact" text={<Icon name="recycle" />} title="Returned Products" disabled extraClass={this.props.extraClass} />
            );
        }
        if (this.props.product.is_dispatched) {
            return (
                <Dropdown id="returndropdownreact" text={<Icon name="recycle" />} title="Returned Products" extraClass={this.props.extraClass}>
                    <button
                        className="dropdown-item"
                        onClick={() => this.props.handleReturn("fault")}
                        role="link"
                    >Fault</button>
                </Dropdown>
            );
        }
        return (
            <Dropdown id="returndropdownreact" text={<Icon name="recycle" />} title="Returned Products" extraClass={this.props.extraClass}>
                <button className="dropdown-item" onClick={() => this.props.handleReturn("unprocessed")} role="link">Un-Processed</button>
                <button className="dropdown-item" onClick={() => this.props.handleReturn("semiprocessed")} role="link">Semi-Processed</button>
                <button className="dropdown-item" onClick={() => this.props.handleReturn("mistake")} role="link">Cutting Mistake</button>
            </Dropdown>
        );
    }
}

class ProductActionBar extends React.Component {
    render() {
        return (
            <div className="d-flex flex-row justify-content-end">
                <CompleteButton 
                    product={this.props.product}
                    handleComplete={this.props.handleComplete}
                    handleUncomplete={this.props.handleUncomplete}
                    isLoading={this.props.isLoadingComplete}
                    extraClass="mr-1"
                />
                <ReturnButton
                    product={this.props.product}
                    handleReturn={this.props.handleReturn}
                    isLoading={this.props.isLoadingReturn}
                />
            </div>
        );
    }
}

class ProductOrderTD extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <td className="product-order_number">
                <a href={this.props.product.absolute_url}>{this.props.product.order_number}</a>
            </td>
        )
    }
}

class ProductQtyTD extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <td className="product-qty">{this.props.product.quantity}</td>
        );
    }
}

class ProductSizeTD extends React.Component {
    render() {
        return (
            <td className="product-size">{this.props.product.size}</td>
        );
    }
}

class ProductFabricTD extends React.Component {
    render() {
        return (
            <td className="product-fabric">{this.props.product.fabric}</td>
        );
    }
}

class ProductColorTD extends React.Component {
    render() {
        return (
            <td className="product-color">{this.props.product.color}</td>
        );
    }
}

class ProductAssignedToTD extends React.Component {
    render() {
        return (
            <td className="product-assignedto">{this.props.product.assignedto}</td>
        );
    }
}

class ProductCompletedByTD extends React.Component {
    render() {
        return (
            <td className="product-completedby">{this.props.product.completedby}</td>
        );
    }
}

class ProductDateCompletedTD extends React.Component {
    render() {
        return (
            <td className="product-date_completed">{this.props.product.date_completed}</td>
        );
    }
}

class ProductStatusTD extends React.Component {
    render() {
        var bg = "";
        if (this.props.product.is_assigned) {
            bg = "bg-warning";
        }
        else if (this.props.product.is_dispatched) {
            bg = "bg-dark text-light";
        }
        else if (this.props.product.is_completed) {
            bg = "bg-success text-light";
        }
        else if (this.props.product.is_returned) {
            bg = "bg-danger";
        }
        return (
            <td className={bg}>{this.props.product.status}</td>
        );
    }
}

class ProductActionTD extends React.Component {
    render() {
        return (
            <td className="product-action">
                <ProductActionBar product={this.props.product} 
                    handleComplete={this.props.handleComplete}
                    handleUncomplete={this.props.handleUncomplete}
                    handleReturn={this.props.handleReturn}
                    isLoadingComplete={this.props.isLoadingComplete}
                    isLoadingReturn={this.props.isLoadingReturn}
                />
            </td>
        );
    }
}

class ProductTR extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            product: this.props.product,
            isLoadingComplete: false,
            isLoadingReturn: false,
        }
    }

    getProduct = () => {
        var product;
        $.ajax({
            type: "GET",
            async: false,
            data: {},
            url: this.props.product.json_url,
            success: (result) => {
                product = JSON.parse(result.product);
            }
        });
        return product;
    }

    handleComplete = () => {
        this.setState({isLoadingComplete: true});
        $.ajax({
            type: "POST",
            async: true,
            data: {},
            url: this.state.product.complete_url,
            success: (result) => {
                this.setState({
                    product: this.getProduct(),
                    isLoadingComplete: false,
                });
            },
            failure: (reason) => {
                this.setState({isLoadingComplete: false});
            }
        });
    }

    handleUncomplete = () => {
        this.setState({isLoadingComplete: true});
        $.ajax({
            type: "POST",
            async: true,
            data: {},
            url: this.state.product.uncomplete_url,
            success: (result) => {
                this.setState({
                    product: this.getProduct(),
                    isLoadingComplete: false,
                });
            },
            failure: (reason) => {
                this.setState({isLoadingComplete: false});
            }
        });
    }

    handleReturn = (remark) => {
        this.setState({isLoadingReturn: true})
        $.ajax({
            type: "POST",
            async: true,
            data: {'return_remark': remark},
            url: this.state.product.return_url,
            success: (result) => {
                this.setState({
                    product: this.getProduct(),
                    isLoadingReturn: false,
                });
            },
            failure: (reason) => {
                this.setState({
                    isLoadingReturn: false,
                });
            }
        });
    }

    render() {
        return (
            <tr>
                <ProductOrderTD product={this.state.product} />
                <ProductQtyTD product={this.state.product} />
                <ProductSizeTD product={this.state.product} />
                <ProductFabricTD product={this.state.product} />
                <ProductColorTD product={this.state.product} />
                <ProductAssignedToTD product={this.state.product} />
                <ProductCompletedByTD product={this.state.product} />
                <ProductDateCompletedTD product={this.state.product} />
                <ProductStatusTD product={this.state.product} />
                <ProductActionTD product={this.state.product} 
                    handleComplete={this.handleComplete}
                    handleUncomplete={this.handleUncomplete}
                    handleReturn={this.handleReturn}
                    isLoadingComplete={this.state.isLoadingComplete}
                    isLoadingReturn={this.state.isLoadingReturn}
                />
            </tr>
        );
    }
}

class ProductTBody extends React.Component {
    constructor(props) {
        super(props);
        // this.productList = this.fetchProductList(this.props.kitID, this.props.page);
    }

    // componentDidUpdate = () => {
    //     this.productList = this.fetchProductList(this.props.kitID, this.props.page);
    // }

    fetchProductList = (kitID, page) => {
        var ret;
        $.ajax({
            type: "GET",
            async: false,
            data: {},
            url: "/kit/" + kitID + "/view/ajax/?page=" + page,
            success: (result) => {
                ret = result.context;
            },
            failure: (reason) => {
                alert('ajax failed');
            }
        });
        return ret;
    }

    render() {
        // var pl = this.productList;
        var productItems = this.fetchProductList(this.props.kitID, this.props.page).map((i) => {
        // var productItems = pl.map((i) => {
            return (
                <ProductTR key={i.id} product={i} />
            );
        });
        return (
            <tbody>
                {productItems}
            </tbody>
        );
    }
}

class ProductTHead extends React.Component {
    render() {
        return (
            <thead className="bg-dark text-light font-weight-bold">
                <tr>
                    <th>Order #</th>
                    <th>Qty</th>
                    <th>Sq.Ft.</th>
                    <th>Fabric</th>
                    <th>Color</th>
                    <th>Assigned To</th>
                    <th>Completed By</th>
                    <th>Completion Date</th>
                    <th>Status</th>
                    <th></th>
                </tr>
            </thead>
        );
    }
}

class ProductTable extends React.Component {
    render() {
        return (
            <table className="table table-hover table-sm table-striped text-center">
                <ProductTHead />
                <ProductTBody kitID={this.props.kitID} page={this.props.page} />
            </table>
        );
    }
}

class Pagination extends React.Component {
    constructor(props) {
        super(props);
    }

    range = (from, to, step=1) => {
        let i = from;
        const range = [];
        while (i <= to) {
            range.push(i);
            i += step;
        }
        return range;
    }

    getPages = () => {
        var r = this.range(1, this.props.totalPages);
        return r.map((i) => {
            let cn = "page-item";
            if (i == this.props.currentPage) {
                cn += " active";
            }
            return (
                <li className={cn} key={i}>
                    <a href="" className="page-link" onClick={e => this.props.gotoPage(e, i)}>{i}</a>
                </li>
            );
        });
    }

    render() {
        var prevClassName = "page-item"
        var nextClassName = "page-item"
        if (this.props.currentPage == 1) {
            prevClassName += " disabled";
        }
        else if (this.props.currentPage == this.props.totalPages) {
            nextClassName += " disabled";
        }
        return (
            <nav aria-label="Pagination Nav">
                <ul className="pagination justify-content-end">
                    <li className={prevClassName} key={-1}>
                        <a className="page-link" href="" onClick={e => this.props.gotoPage(e, this.props.currentPage-1)}>&laquo;</a>
                    </li>
                    {this.getPages()}
                    <li className={nextClassName} key={-2}>
                        <a className="page-link" href="" onClick={e => this.props.gotoPage(e, this.props.currentPage+1)}>&raquo;</a>
                    </li>
                </ul>
            </nav>
        );
    }
}

class PaginatedTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentPage: this.props.currentPage,
        }
    }

    gotoPage = (event, page) => {
        console.log(this.state.currentPage);
        this.setState({
            currentPage: page,
        });
        event.preventDefault();
    }

    render() {
        return (
            <div className="mt-1 table-responsive">
                <ProductTable kitID={this.props.kitID} page={this.state.currentPage} />
                <Pagination 
                    currentPage={this.state.currentPage}
                    totalPages={this.props.totalPages}
                    gotoPage={this.gotoPage}
                />
            </div>
        );
    }
}

document.querySelectorAll('.react_action_container').forEach(
    domContainer => {
        const kit_id = parseInt(domContainer.dataset.kitid)
        const currentPage = parseInt(domContainer.dataset.currentpage);
        const totalPages = parseInt(domContainer.dataset.totalpages);
        ReactDOM.render(<PaginatedTable kitID={kit_id} currentPage={currentPage} totalPages={totalPages}/>, domContainer);
    }
);