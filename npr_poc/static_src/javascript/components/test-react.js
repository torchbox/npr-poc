//Tests that react is working in a new build

import * as React from 'react';

export default class TestReact extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            greeting: props.greeting,
        };
    }

    render() {
        return (
            <div>

                <p className="test">The greeting is {this.state.greeting}</p>
            </div>
        );
    }
}