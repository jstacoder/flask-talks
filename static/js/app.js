var app = angular.module('app',[]);

app.directive('getHidden',function(){
    return {
        restrict:"A",
        require:"ngModel",
        link:function(scope,ele,attrs,ctrl){
            ctrl.$setViewValue(ele.val());
        }
    };
});

app.service('talkHolder',talkHolder);


function talkHolder(){
    var self = this;
    self.talk = false;
    self.getTalk = function(){
        return self.talk;
    };
    self.setTalk = function(talk){
        self.talk = talk;
    };
};

app.directive('addInput',addInput);


addInput.$inject = ['$document'];

function addInput($document){
    return {
        restrict:'A',
        scope:{
            type:"@"
        },
        require:'addInput',
        controller:['$document',function($scope,$ele,$attrs,$document){
            var self = this;

            self.getInput = function(type){
                var input = document.createElement('input');
                input.setAttribute('type',type);
                return input;
            }
        }],
        link:addInputLinkFn
    };
};

function addInputLinkFn(scope,ele,attrs,ctrl){
    ele.on("click",function(){        
        if(!attrs.type){
            var type = 'text';
        }else{
            var type = attrs.type;
        }
        scope.type = type;

        var input = angular.element(ctrl.getInput(type));
        input.addClass('form-control');

        var div = angular.element(document.createElement('div'));
        div.addClass('form-group');

        var label = angular.element(document.createElement('label'));
        label.addClass('control-label');
        label.text('Topic Title');

        var btn = angular.element(document.createElement('button'));
        btn.addClass('btn');
        btn.addClass('btn-secondary-outline');
        btn.text('Add Subtopic');
        btn[0].setAttribute('ng-click','addSubtopic(data.sub)');

        div.append(label);
        div.append(input);
        ele.after(div);
        div.after(btn);

    });
};

app.controller('AddContentCtrl',['$window','$http','$scope',function($window,$http,$scope){
    var self = this;

    $scope.addContent = {
        content:'',
        bullet:'',
        sub:'',
        typecode:'',
        order:0
    };

    self.submit = function(form){
        console.log($scope);
        var type_code = form.type_code.$viewValue,
            content = form.content.$viewValue,
            order = form.order.$viewValue,
            bullet = form.bullet.$viewValue,
            sub_id = form.sub.$viewValue;
        console.log(form);

        $http.post('/talks/content/add/'+sub_id+'/',{content:content,bullet:bullet,type_code:type_code,order:order}).then(function(res){
            $window.location.href = '/talks/view/sub/'+sub_id;
        });                                
    }
}]);

//app.controller('TopicCtrl',TopicCtrl);

app.controller('TalkCtrl',TalkCtrl);

TalkCtrl.$inject = ['$scope','$http','talkHolder','$window'];

function TalkCtrl($scope,$http,talkHolder,$window){
    console.log('im  here');

    $scope.addTopic = function(){
        document.forms[0].submit();
    }

    $scope.addSubtopic = function(name){
        console.log('starting post request');
        $http.post('/api/v1/subtopics/add/',{name:name}).then(function(res){
                console.log('FINISHED adding sub',res.data);
        });
    }
    
    $scope.addTalk = function(name){
        if(!talkHolder.getTalk()){
            $http.post('/api/v1/talks/add/',{name:name}).then(function(res){
                console.log('FINISHED',res);
                talkHolder.setTalk(res.data);
                $scope.talk = {};
                $scope.talk.name = res.data.talk.name;
                $window.location.href = '/talks/';
            });
        }
    };

    $http.get('/api/v1/talks/').then(function(res){
        $scope.data = res.data;
    });
};
