let changesMockup = [
    {
        policy: 'ADD',
        table: 'LocateAllCourses',
        constraint: {
            is_active: false,
            comment: 'Just trying something here',
            weeks: [1,2,5],
            parameters: [
                {   
                    name: 'department',
                    param: {
                        name: 'department',
                        required: true,
                        type: 'base.department',
                        id_list: [8,9,10],
                        acceptable: [40, 50],
                    }
                },
                {
                    name: 'pre_assigned_only',
                    required: true,
                    type: 'BooleanField',
                },
            ],
        }
    },
    {
        policy: 'DELETE',
        table: 'GroupsLunchBreak',
        id: 2,
    },
    {
        policy: 'EDIT',
        table: 'StabilizeTutorsCourses',
        id: 1,
        constraint: {
            comment: "Comment changed",
            is_active: false,
            weeks: [
                {
                    action: 'ADD',
                    values: [6,7,8],
                },
                {
                    action: 'DELETE',
                    values: [1,2,3],
                },
            ],
            parameters: [
                {   
                    action: 'ADD',
                    name: 'department',
                    param: {
                        required: true,
                        type: 'base.department',
                        id_list: [8,9,10],
                        acceptable: [40, 50],
                    }
                },
                {   
                    action: 'DELETE',
                    name: 'department',
                },
                {   
                    action: 'EDIT',
                    name: 'join2courses',
                    param: {
                        required: true,
                        // type: 'BooleanField', probably delete and add ?
                        id_list: [
                            {
                                action: 'ADD',
                                values: [6,7,8],
                            },
                            {
                                action: 'DELETE',
                                values: [1,2,3],
                            },
                        ],
                        acceptable: [
                            {
                                action: 'EMPTY',
                            },
                        ],
                    }
                },
            ]
        }
    }
]