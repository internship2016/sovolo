var gulp = require('gulp-help')(require('gulp'));
var sass = require('gulp-sass');
var less = require('gulp-less');
var notify = require('gulp-notify');
var bower = require('gulp-bower');
var gf = require('gulp-filter');
var mainBowerFiles = require('main-bower-files');
var debug = require('gulp-debug');
var rimraf = require('rimraf');
var cleanCSS = require('gulp-clean-css');
var runSequence = require('run-sequence');

var bowerDir = './bower_components';
var conf = {
  sassPath: './static/sass',
  scriptPath: './static/script',
  bowerDir: bowerDir,
  bootstrapDir: bowerDir + '/bootstrap-sass',
  bootstrapDatetimepickerDir: bowerDir + '/eonasdan-bootstrap-datetimepicker'
};

var filter = {
  js: gf('**/*.js', {restore: true}),
  css: gf('**/*.css', {restore: true}),
  less: gf('**/*.less', {restore: true}),
  scss: gf('**/*.scss', {restore: true}),
  fonts: gf([
    '**/*.eot',
    '**/*.woff',
    '**/*.woff2',
    '**/*.svg',
    '**/*.ttf'
  ], {restore: true})
};

gulp.task('bower.install', 'ネットからbower_componentsに持ってくる', function () {
  return bower().pipe(gulp.dest(conf.bowerDir));
});

// TODO: minify/uglify/etc
gulp.task('bower.copy', 'bower_componentsからstaticに必要なファイルをコピーする', ['bower.install'], function () {
  return gulp.src(
    mainBowerFiles({
      debugging: true,
      checkExistence: true,
      overrides: {
        'bootstrap': {
          main: [
            './dist/js/bootstrap.js',
            './dist/css/*.min.*',
            './dist/fonts/*.*'
          ]
        },
        'font-awesome': {
          main: [
            './css/*.min.*',
            './fonts/*.*'
          ]
        },
        'moment': {
          main: [
            './moment.js',
            './min/moment-with-locales.js'
          ]
        }
      }
    })
  )

  .pipe(filter.js)
  .pipe(gulp.dest('./static/js'))
  .pipe(filter.js.restore)

  .pipe(filter.css)
  .pipe(gulp.dest('./static/css'))
  .pipe(filter.css.restore)

  .pipe(filter.less)
  .pipe(less())
  .pipe(gulp.dest('./static/css'))
  .pipe(filter.less.restore)

  .pipe(filter.fonts)
  .pipe(gulp.dest('./static/fonts'))
  .pipe(filter.fonts.restore)

  ;
});

gulp.task('bower', 'bower install and copy', function (cb) {
  runSequence(['bower.install', 'bower.copy'], cb);
});

gulp.task('css.bootstrap', 'カスタムbootstrapを作る', function () {
  return gulp.src(conf.sassPath + '/bootstrap/*.scss/')
    .pipe(sass({
      includePaths: [
        conf.bootstrapDir + '/assets/stylesheets',
        conf.bootstrapDatetimepickerDir + '/src/sass'
      ]
    }))
    .pipe(cleanCSS())
    .pipe(gulp.dest('./static/css'));
});

// Watch static/sass/style.scss,
// Compress all sass files into css
gulp.task('css', 'scssファイルをstatic/cssに移す', ['css.bootstrap'], function () {
  return gulp.src(conf.sassPath + '/*.scss')
    .pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
    .pipe(gulp.dest('./static/css'));
});

gulp.task('js', 'jsファイルをstatic/jsに移す', function () {
  return gulp.src(conf.scriptPath + '/*.js')
    .pipe(gulp.dest('./static/js'));
});

gulp.task('watch', 'scssとjsファイルを監視して適時コピーする', function () {
  gulp.watch(conf.sassPath + '/**/*.scss', ['css']);
  gulp.watch(conf.scriptPath + '/**/*.js', ['js']);
});

gulp.task('clean', '全部消す', function (cb) {
  return rimraf('./static/{js,css,fonts}', cb);
});

gulp.task('default', 'リビルド', function (cb) {
  runSequence('clean', ['bower', 'css', 'js'], cb);
});
