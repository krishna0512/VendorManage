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
    render() {
        return (
            <td className="product-order_number">
                <a href={this.props.product.absolute_url}>{this.props.product.order_number}</a>
            </td>
        )
    }
}

class ProductQtyTD extends React.Component {
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
            <td className="product-color">
                <span className={"dot align-middle color-"+this.props.product.color}></span>
                {this.props.product.color.replace('_', ' ')}
            </td>
        );
    }
}

class ProductAssignedToTD extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        var text;
        if (this.props.product.assignedto == null) {
            text = "Assign To";
        }
        else {
            text = this.props.product.assignedto.username;
        }
        var workerItems = this.props.workerList.map(i => {
            return (
                <a key={i.id}
                    className="dropdown-item"
                    role="link"
                    onClick={() => this.props.handleAssign(i.id)}
                >
                    {i.username}
                </a>
            )
        });
        return (
            <td className="product-assignedto">
                <Dropdown text={text}>
                    <a key="0"
                        className="dropdown-item"
                        role="link"
                        onClick={() => this.props.handleAssign(0)}
                    >---</a>
                    {workerItems}
                </Dropdown>
            </td>
        );
    }
}

class ProductCompletedByTD extends React.Component {
    render() {
        return (
            <td className="product-completedby">{this.props.product.completedby ? this.props.product.completedby.username : "None"}</td>
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
            <td className={"product-status "+bg}>{this.props.product.status}</td>
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
            product: undefined,
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
            url: this.props.productURL,
            success: (result) => {
                product = result;
            }
        });
        return product;
    }

    componentDidMount() {
        fetch(this.props.productURL).then(res => res.json()).then(response => {
            this.setState({
                product: response,
            });
        });
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

    handleAssign = (workerID) => {
        $.ajax({
            type: "POST",
            async: true,
            data: {'worker_id': workerID},
            url: this.state.product.assign_url,
            success: (result) => {
                this.setState({
                    product: this.getProduct(),
                });
            },
            failure: (reason) => {
                alert(reason);
            },
        });
    }

    render() {
        if (this.state.product == undefined) {
            return (
                <tr>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                    <td>---</td>
                </tr>
            );
        }
        return (
            <tr>
                <ProductOrderTD product={this.state.product} />
                <ProductQtyTD product={this.state.product} />
                <ProductSizeTD product={this.state.product} />
                <ProductFabricTD product={this.state.product} />
                <ProductColorTD product={this.state.product} />
                <ProductAssignedToTD product={this.state.product} 
                    handleAssign={this.handleAssign}
                    workerList={this.props.workerList}
                />
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
    }

    fetchProductList = () => {
        var ret;
        $.ajax({
            type: "GET",
            async: false,
            data: {},
            url: this.props.kitURL,
            success: (result) => {
                ret = result.products;
            },
            failure: (reason) => {
                alert('ajax failed');
            }
        });
        return ret;
    }

    fetchWorkerList = () => {
        var ret;
        $.ajax({
            type: "GET",
            data: {},
            async: false,
            url: '/worker/api/',
            success: (result) => {
                ret = result;
            },
            failure: (reason) => {
                alert(reason);
            }
        });
        return ret;
    }

    render() {
        // var productItems;
        // fetch(this.props.kitURL).then(res => res.json()).then(res => {
        //     var pi = [];
        //     for (var i=0; i<res.products.length; i++) {
        //         pi.push(<ProductTR key={i} productURL={res.products[i]} />);
        //     }
        //     productItems = res.products.map((productURL) => {
        //         return (
        //             <ProductTR
        //                 key={productURL}
        //                 productURL={productURL}
        //             />
        //         );
        //     });
        // });
        // var productItems = this.fetchProductList().map(
        //     i => <ProductTR key={i.id} productURL={i.api_url} />
        // );
        var workerList = this.fetchWorkerList();
        var productItems = this.props.productList.map(
            i => <ProductTR key={i.id} productURL={i.api_url} workerList={workerList} />
        );
        // var productItems = this.fetchProductList(this.props.kitID, this.props.page).map((i) => {
        //     return (
        //         <ProductTR key={i.id} product={i} />
        //     );
        // });
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
                <ProductTBody productList={this.props.productList} />
                {/* <ProductTBody kitURL={this.props.kitURL} page={this.props.page} /> */}
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

// class ChangeCompleteDate extends React.Component {
//     constructor(props) {
//         super(props);
//         this.state = {
//             date: this.props.date,
//         }
//     }

//     componentDidMount() {
//         $('#datepicker_product_completion').datepicker({
//             dateFormat: 'yy-mm-dd',
//         });
//     }

//     changeDate = () => {
//         $.ajax({
//             type: "POST",
//             async: false,
//             url: this.props.changeDateURL,
//             data: {'date': $('#datepicker_product_completion').val()},
//             success: (result) => {
//                 this.setState({
//                     date: result['date'],
//                 });
//             }
//         });
//     }

//     render() {
//         return (
//             <div className="d-flex">
//                 <div className="mr-auto text-muted">
//                     Product Completion Date 
//                     <div className="input-group input-group-sm">
//                         <input type="text" className="form-control" id="datepicker_product_completion" placeholder={this.state.date} aria-describedby="button23"></input>
//                         <div className="input-group-append">
//                             <button className="btn btn-outline-primary" id="button23" onClick={this.changeDate}>Done</button> 
//                         </div>
//                     </div>
//                 </div>
//             </div>
//         );
//     }
// }

class PageSize extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                Show&nbsp;
                <select value={this.props.pageSize} onChange={e => this.props.changePageSize(e)}
                    className="custom-select custom-select-sm form-control form-control-sm w-auto"
                    id="dropdownnumberrecords"
                >
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50">50</option>
                    <option value="100">100</option>
                </select>
                &nbsp;Entries
            </div>
        );
    }
}

class TableHeader extends React.Component {
    render() {
        return (
            <div className="d-flex table-header">
                <PageSize changePageSize={this.props.changePageSize} pageSize={this.props.pageSize} />
            </div>
        );
    }
}

class PaginatedTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            kit: this.getKit(),
            currentPage: 1,
            pageSize: 10,
        }
    }

    getKit = (page=1, size=10) => {
        var ret;
        $.ajax({
            type: "GET",
            data: {'page': page, 'page_size': size},
            async: false,
            url: this.props.kitURL,
            success: (result) => {
                ret = result;
            },
            failure: (reason) => {
                alert(reason);
            }
        });
        return ret;
    }

    gotoPage = (event, page) => {
        this.setState((state, props) => ({
            currentPage: page,
            kit: this.getKit(page, state.pageSize),
        }));
        event.preventDefault();
    }

    changePageSize = (event) => {
        // No Idea why I have to use the nativeEvent?
        var x = event.nativeEvent.target.value;
        this.setState((state, props) => ({
            pageSize: x,
            currentPage: 1,
            kit: this.getKit(1, x),
        }));
        event.preventDefault();
    }

    render() {
        return (
            <div className="mt-1 table-responsive">
                {/* <ChangeCompleteDate date={this.props.kit.date_product_completion} changeDateURL={this.props.kit.change_completion_date_url} /> */}
                {/* <ProductTable kitID={this.props.kit.id} page={this.state.currentPage} /> */}
                <TableHeader changePageSize={this.changePageSize} pageSize={this.state.pageSize} />
                <ProductTable productList={this.state.kit.products.results} />
                <Pagination 
                    currentPage={this.state.currentPage}
                    totalPages={this.state.kit.products.num_pages}
                    gotoPage={this.gotoPage}
                />
            </div>
        );
    }
}

var root = document.getElementById('root');
ReactDOM.render(
    <PaginatedTable kitURL={root.dataset.url} />,
    root
);

// document.querySelectorAll('.react_action_container').forEach(
//     domContainer => {
//         const kit = JSON.parse(domContainer.dataset.kit);
//         const currentPage = parseInt(domContainer.dataset.currentpage);
//         const totalPages = parseInt(domContainer.dataset.totalpages);
//         const date = domContainer.dataset.completiondate;
//         ReactDOM.render(<PaginatedTable kit={kit} currentPage={currentPage} totalPages={totalPages} date={date} />, domContainer);
//     }
// );